from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    balance = Column(Float, default=1000.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    markets = relationship("Market", back_populates="creator")
    positions = relationship("Position", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolution_date = Column(DateTime, nullable=False)
    resolved = Column(Boolean, default=False)
    outcome = Column(Boolean, nullable=True)
    liquidity_param = Column(Float, default=100.0)
    q_yes = Column(Float, default=0.0)
    q_no = Column(Float, default=0.0)

    creator = relationship("User", back_populates="markets")
    positions = relationship("Position", back_populates="market")
    transactions = relationship("Transaction", back_populates="market")


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        UniqueConstraint("user_id", "market_id", name="uq_user_market"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    shares_yes = Column(Float, default=0.0)
    shares_no = Column(Float, default=0.0)

    user = relationship("User", back_populates="positions")
    market = relationship("Market", back_populates="positions")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    action = Column(String(10), nullable=False)  # buy or sell
    outcome = Column(String(5), nullable=False)  # yes or no
    shares = Column(Float, nullable=False)
    price_per_share = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    market = relationship("Market", back_populates="transactions")
