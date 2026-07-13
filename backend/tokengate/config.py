import os

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID", "")  # e.g. -1001234567890
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

# Ethereum
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "")  # e.g. https://eth-mainnet.g.alchemy.com/v2/KEY
NFT_CONTRACT_ADDRESS = os.getenv("NFT_CONTRACT_ADDRESS", "")
MIN_NFT_BALANCE = int(os.getenv("MIN_NFT_BALANCE", "1"))

# App
# Public base URL of this server, used to build the wallet-verification link
# sent to users by the bot (no trailing slash).
TOKENGATE_BASE_URL = os.getenv("TOKENGATE_BASE_URL", "http://localhost:8000").rstrip("/")
RECHECK_INTERVAL_HOURS = float(os.getenv("RECHECK_INTERVAL_HOURS", "6"))
INVITE_LINK_TTL_MINUTES = int(os.getenv("INVITE_LINK_TTL_MINUTES", "15"))
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "60"))

GROUP_NAME = os.getenv("TOKENGATE_GROUP_NAME", "NFT Holders")


def is_configured() -> bool:
    return bool(
        TELEGRAM_BOT_TOKEN
        and TELEGRAM_GROUP_ID
        and ETH_RPC_URL
        and NFT_CONTRACT_ADDRESS
    )
