import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from tokengate import config
from tokengate.eth import build_sign_message, nft_balance, recover_signer
from tokengate.models import GateMember
from tokengate.telegram_api import create_one_time_invite, send_message

router = APIRouter(tags=["tokengate"])


def require_configured():
    if not config.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Token gate is not configured (set TELEGRAM_BOT_TOKEN, "
            "TELEGRAM_GROUP_ID, ETH_RPC_URL and NFT_CONTRACT_ADDRESS)",
        )


def _new_session(member: GateMember):
    member.session_token = secrets.token_urlsafe(32)
    member.nonce = secrets.token_hex(16)
    member.session_created_at = datetime.utcnow()


def _session_expired(member: GateMember) -> bool:
    if not member.session_created_at:
        return True
    age = datetime.utcnow() - member.session_created_at
    return age > timedelta(minutes=config.SESSION_TTL_MINUTES)


# ---------------------------------------------------------------------------
# Telegram webhook
# ---------------------------------------------------------------------------

@router.post("/api/tokengate/telegram/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str = Header(default=""),
):
    require_configured()
    if config.TELEGRAM_WEBHOOK_SECRET and not secrets.compare_digest(
        x_telegram_bot_api_secret_token, config.TELEGRAM_WEBHOOK_SECRET
    ):
        raise HTTPException(status_code=403, detail="Bad webhook secret")

    update = await request.json()
    message = update.get("message")
    if not message or "text" not in message:
        return {"ok": True}

    chat = message["chat"]
    text = message["text"].strip()
    user = message.get("from", {})

    # Setup helper: reply with the chat id when asked inside any group,
    # so the admin can fill in TELEGRAM_GROUP_ID.
    if chat["type"] in ("group", "supergroup"):
        if text.startswith("/chatid"):
            await send_message(chat["id"], f"Chat ID: {chat['id']}")
        return {"ok": True}

    if chat["type"] != "private":
        return {"ok": True}

    if text.startswith("/start"):
        member = (
            db.query(GateMember).filter(GateMember.telegram_id == user["id"]).first()
        )
        if not member:
            member = GateMember(telegram_id=user["id"])
            db.add(member)
        member.telegram_username = user.get("username")
        _new_session(member)
        db.commit()

        verify_url = f"{config.TOKENGATE_BASE_URL}/tokengate/verify?session={member.session_token}"
        await send_message(
            chat["id"],
            f"Welcome! To join the {config.GROUP_NAME} group you need to prove "
            "you hold the NFT.\n\n"
            "Tap the button below, connect your wallet and sign a message "
            "(free, no transaction). If your wallet holds the NFT you'll "
            "receive a personal one-time invite link.",
            reply_markup={
                "inline_keyboard": [[{"text": "🔐 Verify my wallet", "url": verify_url}]]
            },
        )
    else:
        await send_message(chat["id"], "Send /start to verify your wallet and join the group.")

    return {"ok": True}


# ---------------------------------------------------------------------------
# Wallet verification API
# ---------------------------------------------------------------------------

class VerifyRequest(BaseModel):
    session: str
    address: str
    signature: str


@router.get("/api/tokengate/session/{token}")
def get_session(token: str, db: Session = Depends(get_db)):
    require_configured()
    member = db.query(GateMember).filter(GateMember.session_token == token).first()
    if not member or _session_expired(member):
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Send /start to the bot again.",
        )
    return {
        "message": build_sign_message(member.telegram_id, member.nonce),
        "group_name": config.GROUP_NAME,
        "min_balance": config.MIN_NFT_BALANCE,
        "contract": config.NFT_CONTRACT_ADDRESS,
    }


@router.post("/api/tokengate/verify")
async def verify_wallet(data: VerifyRequest, db: Session = Depends(get_db)):
    require_configured()
    member = (
        db.query(GateMember).filter(GateMember.session_token == data.session).first()
    )
    if not member or _session_expired(member):
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Send /start to the bot again.",
        )

    message = build_sign_message(member.telegram_id, member.nonce)
    try:
        signer = recover_signer(message, data.signature)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")
    if signer.lower() != data.address.lower():
        raise HTTPException(status_code=400, detail="Signature does not match the connected wallet")

    # One wallet can only gate one Telegram account.
    taken = (
        db.query(GateMember)
        .filter(
            GateMember.wallet_address == signer.lower(),
            GateMember.telegram_id != member.telegram_id,
            GateMember.status == "verified",
        )
        .first()
    )
    if taken:
        raise HTTPException(
            status_code=409,
            detail="This wallet is already linked to another Telegram account",
        )

    balance = await nft_balance(signer)
    if balance < config.MIN_NFT_BALANCE:
        raise HTTPException(
            status_code=403,
            detail=f"This wallet holds {balance} NFT(s); at least "
            f"{config.MIN_NFT_BALANCE} required",
        )

    member.wallet_address = signer.lower()
    member.status = "verified"
    member.verified_at = datetime.utcnow()
    member.last_checked = datetime.utcnow()
    member.session_token = None  # single-use session
    member.nonce = None
    db.commit()

    invite_link = await create_one_time_invite()
    await send_message(
        member.telegram_id,
        f"✅ Verified! You hold {balance} NFT(s).\n\n"
        f"Here is your personal invite link (valid for "
        f"{config.INVITE_LINK_TTL_MINUTES} minutes, one use):\n{invite_link}",
    )
    return {"ok": True, "balance": balance, "invite_link": invite_link}


# ---------------------------------------------------------------------------
# Verification page (static, reads the session token client-side)
# ---------------------------------------------------------------------------

VERIFY_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wallet verification</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
         background:#0d1117; color:#e6edf3; font-family:system-ui,-apple-system,sans-serif; }
  .card { background:#161b22; border:1px solid #30363d; border-radius:12px;
          padding:32px; max-width:420px; width:90%; text-align:center; }
  h1 { font-size:1.3rem; margin:0 0 8px; }
  p  { color:#8b949e; font-size:.92rem; line-height:1.5; }
  button { background:#238636; color:#fff; border:0; border-radius:8px; padding:12px 24px;
           font-size:1rem; cursor:pointer; width:100%; margin-top:16px; }
  button:disabled { background:#30363d; cursor:default; }
  #status { margin-top:16px; font-size:.9rem; min-height:1.4em; }
  .err { color:#f85149; } .ok { color:#3fb950; }
  a { color:#58a6ff; word-break:break-all; }
  code { background:#0d1117; padding:2px 6px; border-radius:4px; font-size:.8rem; }
</style>
</head>
<body>
<div class="card">
  <h1>🔐 NFT holder verification</h1>
  <p id="intro">Connect your wallet and sign a free message to prove you hold the NFT.
  No transaction is sent.</p>
  <button id="btn">Connect wallet &amp; sign</button>
  <div id="status"></div>
</div>
<script>
const session = new URLSearchParams(location.search).get('session');
const btn = document.getElementById('btn');
const status = document.getElementById('status');

function show(msg, cls) { status.className = cls || ''; status.innerHTML = msg; }

async function run() {
  if (!session) { show('Missing session token. Open this page from the bot link.', 'err'); return; }
  if (!window.ethereum) {
    show('No wallet detected. Open this link in a browser with MetaMask, or use ' +
         'your wallet app\\'s built-in browser.', 'err');
    return;
  }
  btn.disabled = true;
  try {
    show('Loading verification message…');
    const sres = await fetch('/api/tokengate/session/' + encodeURIComponent(session));
    const sbody = await sres.json();
    if (!sres.ok) throw new Error(sbody.detail || 'Session error');

    show('Connecting wallet…');
    const [address] = await window.ethereum.request({ method: 'eth_requestAccounts' });

    show('Please sign the message in your wallet…');
    const hexMsg = '0x' + Array.from(new TextEncoder().encode(sbody.message))
        .map(b => b.toString(16).padStart(2, '0')).join('');
    const signature = await window.ethereum.request({
      method: 'personal_sign', params: [hexMsg, address],
    });

    show('Checking your NFT balance on Ethereum…');
    const vres = await fetch('/api/tokengate/verify', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session, address, signature }),
    });
    const vbody = await vres.json();
    if (!vres.ok) throw new Error(vbody.detail || 'Verification failed');

    show('✅ Verified! Your invite link was sent to you on Telegram.<br><br>' +
         'You can also join directly: <a href="' + vbody.invite_link + '">' +
         vbody.invite_link + '</a>', 'ok');
    btn.style.display = 'none';
  } catch (e) {
    show((e && e.message) ? e.message : 'Something went wrong', 'err');
    btn.disabled = false;
  }
}
btn.addEventListener('click', run);
</script>
</body>
</html>"""


@router.get("/tokengate/verify", response_class=HTMLResponse)
def verify_page():
    require_configured()
    return HTMLResponse(VERIFY_PAGE)
