"""Ethereum helpers: signature verification and ERC-721 balance checks."""
import httpx
from eth_account import Account
from eth_account.messages import encode_defunct

from tokengate import config

# ERC-721 / ERC-20 balanceOf(address) selector
BALANCE_OF_SELECTOR = "0x70a08231"


def build_sign_message(telegram_id: int, nonce: str) -> str:
    """The exact message the user signs in their wallet.

    Signing proves control of the wallet; the nonce ties the signature to a
    single verification session and the telegram_id prevents replaying it
    for another Telegram account.
    """
    return (
        f"{config.GROUP_NAME} — Telegram access verification\n"
        f"Telegram user ID: {telegram_id}\n"
        f"Nonce: {nonce}\n"
        "\n"
        "Signing this message is free and does not send a transaction."
    )


def recover_signer(message: str, signature: str) -> str:
    """Return the checksummed address that signed `message` (EIP-191 personal_sign)."""
    return Account.recover_message(encode_defunct(text=message), signature=signature)


async def nft_balance(address: str) -> int:
    """Call balanceOf(address) on the NFT contract via JSON-RPC eth_call."""
    data = BALANCE_OF_SELECTOR + address.lower().removeprefix("0x").rjust(64, "0")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [
            {"to": config.NFT_CONTRACT_ADDRESS, "data": data},
            "latest",
        ],
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(config.ETH_RPC_URL, json=payload)
        resp.raise_for_status()
        body = resp.json()
    if "error" in body:
        raise RuntimeError(f"RPC error: {body['error']}")
    return int(body["result"], 16)
