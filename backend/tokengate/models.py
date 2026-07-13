from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from database import Base


class GateMember(Base):
    __tablename__ = "gate_members"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    telegram_username = Column(String(64), nullable=True)
    wallet_address = Column(String(42), nullable=True, index=True)

    # Verification session: token identifies the pending session, nonce is
    # embedded in the message the user signs.
    session_token = Column(String(64), unique=True, nullable=True, index=True)
    nonce = Column(String(64), nullable=True)
    session_created_at = Column(DateTime, nullable=True)

    status = Column(String(10), default="pending", nullable=False)  # pending | verified | revoked
    verified_at = Column(DateTime, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
