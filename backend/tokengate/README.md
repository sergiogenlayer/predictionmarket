# Telegram Token Gate (Ethereum NFT holders)

Token-gates a private Telegram group behind an Ethereum NFT (ERC-721). Users
prove wallet ownership by signing a message (free, no transaction), the server
checks `balanceOf` on-chain, and holders receive a personal single-use invite
link. A background job re-checks balances periodically and kicks members who
no longer hold the NFT.

## How it works

1. User sends `/start` to your bot → bot replies with a verification link.
2. The link opens `/tokengate/verify`, where the user connects MetaMask (or a
   wallet-app browser) and signs a nonce-based message.
3. The server recovers the signer address from the signature, calls
   `balanceOf(address)` on the NFT contract via JSON-RPC, and if the balance
   meets the minimum, creates a **single-use, short-lived** invite link and
   DMs it to the user.
4. Every `RECHECK_INTERVAL_HOURS`, the server re-checks every verified
   member's balance and removes members who sold/transferred their NFT (they
   can rejoin by re-verifying with `/start`).

## Setup

### 1. Create the bot

1. Open Telegram, talk to [@BotFather](https://t.me/BotFather), send `/newbot`.
2. Pick a name and username; save the **bot token**.
3. Optional: `/setuserpic`, `/setdescription`.

### 2. Create the private group

1. Create a Telegram group and set it to **private** (Group Settings → Group
   Type → Private). Don't share its invite link anywhere.
2. Add your bot to the group and promote it to **admin** with at least:
   *Invite users via link* and *Ban users*.
3. Send `/chatid` inside the group — the bot replies with the group's chat ID
   (looks like `-1001234567890`). That's your `TELEGRAM_GROUP_ID`.
   (This works once the webhook from step 4 is set; alternatively get the ID
   from `https://api.telegram.org/bot<TOKEN>/getUpdates`.)

### 3. Configure environment variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | yes | Token from BotFather |
| `TELEGRAM_GROUP_ID` | yes | Private group chat ID (e.g. `-1001234567890`) |
| `ETH_RPC_URL` | yes | Ethereum mainnet RPC (Alchemy/Infura/etc.) |
| `NFT_CONTRACT_ADDRESS` | yes | Your ERC-721 contract address |
| `TOKENGATE_BASE_URL` | yes (prod) | Public URL of this server, e.g. `https://yourapp.onrender.com` |
| `TELEGRAM_WEBHOOK_SECRET` | recommended | Random string; Telegram echoes it on each webhook call so nobody else can post fake updates |
| `MIN_NFT_BALANCE` | no (1) | Minimum NFTs required |
| `RECHECK_INTERVAL_HOURS` | no (6) | How often to re-verify holders |
| `INVITE_LINK_TTL_MINUTES` | no (15) | Invite link expiry |
| `SESSION_TTL_MINUTES` | no (60) | Wallet-verification session expiry |
| `TOKENGATE_GROUP_NAME` | no | Group name used in bot messages |

The gate activates automatically when the four required variables are set;
otherwise its endpoints return 503 and the rest of the app is unaffected.

### 4. Register the webhook

After deploying with the env vars set:

```bash
cd backend
python -m tokengate.set_webhook
```

This points Telegram at `{TOKENGATE_BASE_URL}/api/tokengate/telegram/webhook`.

### 5. Onboard your holders

Share your bot's link (`https://t.me/YourBot`) — **not** the group link. Each
holder does `/start` → verifies → gets their own one-time invite.

## Security notes

- The signed message embeds the Telegram user ID and a random nonce, so a
  signature can't be replayed for another account or session.
- Sessions are single-use and expire after `SESSION_TTL_MINUTES`.
- One wallet can only be linked to one Telegram account.
- Invite links are single-use (`member_limit=1`) and expire quickly.
- Set `TELEGRAM_WEBHOOK_SECRET` in production so only Telegram can call the
  webhook endpoint.
