"""One-off script: register this server's webhook with Telegram.

Usage (after exporting the tokengate env vars):
    python -m tokengate.set_webhook
"""
import asyncio

from tokengate import config
from tokengate.telegram_api import tg_call


async def main():
    if not config.TELEGRAM_BOT_TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN first")
    url = f"{config.TOKENGATE_BASE_URL}/api/tokengate/telegram/webhook"
    params = {"url": url, "allowed_updates": ["message"]}
    if config.TELEGRAM_WEBHOOK_SECRET:
        params["secret_token"] = config.TELEGRAM_WEBHOOK_SECRET
    await tg_call("setWebhook", **params)
    info = await tg_call("getWebhookInfo")
    print(f"Webhook set to: {info.get('url')}")
    if info.get("last_error_message"):
        print(f"Last error: {info['last_error_message']}")


if __name__ == "__main__":
    asyncio.run(main())
