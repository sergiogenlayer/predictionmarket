"""Thin async wrapper over the Telegram Bot API."""
import time

import httpx

from tokengate import config

API_BASE = "https://api.telegram.org"


async def tg_call(method: str, **params):
    url = f"{API_BASE}/bot{config.TELEGRAM_BOT_TOKEN}/{method}"
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(url, json=params)
        body = resp.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {body.get('description')}")
    return body["result"]


async def send_message(chat_id, text: str, reply_markup: dict | None = None):
    params = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if reply_markup:
        params["reply_markup"] = reply_markup
    return await tg_call("sendMessage", **params)


async def create_one_time_invite() -> str:
    """Single-use invite link to the gated group, expiring after a short TTL."""
    result = await tg_call(
        "createChatInviteLink",
        chat_id=config.TELEGRAM_GROUP_ID,
        member_limit=1,
        expire_date=int(time.time()) + config.INVITE_LINK_TTL_MINUTES * 60,
    )
    return result["invite_link"]


async def kick_member(user_id: int):
    """Remove a user from the group without banning them permanently,
    so they can rejoin later if they re-verify."""
    await tg_call("banChatMember", chat_id=config.TELEGRAM_GROUP_ID, user_id=user_id)
    await tg_call(
        "unbanChatMember",
        chat_id=config.TELEGRAM_GROUP_ID,
        user_id=user_id,
        only_if_banned=True,
    )
