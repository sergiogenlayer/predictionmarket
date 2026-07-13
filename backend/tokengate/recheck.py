"""Periodic re-verification: kick members who no longer hold the NFT."""
import asyncio
import logging
from datetime import datetime

from database import SessionLocal
from tokengate import config
from tokengate.eth import nft_balance
from tokengate.models import GateMember
from tokengate.telegram_api import kick_member, send_message

logger = logging.getLogger("tokengate")


async def recheck_all_members():
    db = SessionLocal()
    try:
        members = db.query(GateMember).filter(GateMember.status == "verified").all()
        for member in members:
            try:
                balance = await nft_balance(member.wallet_address)
            except Exception as exc:
                # RPC hiccup: skip this round rather than kicking on bad data
                logger.warning("Balance check failed for %s: %s", member.wallet_address, exc)
                continue

            member.last_checked = datetime.utcnow()
            if balance < config.MIN_NFT_BALANCE:
                logger.info(
                    "Revoking telegram_id=%s wallet=%s (balance=%s)",
                    member.telegram_id, member.wallet_address, balance,
                )
                member.status = "revoked"
                db.commit()
                try:
                    await kick_member(member.telegram_id)
                    await send_message(
                        member.telegram_id,
                        f"You were removed from {config.GROUP_NAME} because your "
                        "wallet no longer holds the required NFT. If you get it "
                        "back, send /start to re-verify.",
                    )
                except Exception as exc:
                    logger.warning("Kick failed for %s: %s", member.telegram_id, exc)
            else:
                db.commit()
    finally:
        db.close()


async def recheck_loop():
    interval = config.RECHECK_INTERVAL_HOURS * 3600
    while True:
        try:
            await recheck_all_members()
        except Exception:
            logger.exception("Recheck round failed")
        await asyncio.sleep(interval)
