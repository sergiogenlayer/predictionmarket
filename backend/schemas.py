from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# Auth schemas
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Market schemas
class MarketCreate(BaseModel):
    title: str = Field(min_length=10, max_length=200)
    description: str = Field(default="", max_length=2000)
    resolution_date: datetime
    liquidity_param: float = Field(default=100.0, gt=0, le=1000)


class MarketResponse(BaseModel):
    id: int
    title: str
    description: str
    creator_id: int
    creator_username: Optional[str] = None
    created_at: datetime
    resolution_date: datetime
    resolved: bool
    outcome: Optional[bool] = None
    price_yes: float
    price_no: float
    q_yes: float
    q_no: float
    liquidity_param: float
    total_volume: Optional[float] = None

    class Config:
        from_attributes = True


# Trade schemas
class TradeRequest(BaseModel):
    outcome: Literal["yes", "no"]
    action: Literal["buy", "sell"]
    shares: float = Field(gt=0, le=10000)


class TradeResponse(BaseModel):
    message: str
    cost: float
    new_balance: float
    price_yes: float
    price_no: float
    position_yes: float
    position_no: float


class ResolveRequest(BaseModel):
    outcome: bool


# Position schemas
class PositionResponse(BaseModel):
    market_id: int
    market_title: str
    shares_yes: float
    shares_no: float
    current_price_yes: float
    current_price_no: float
    market_resolved: bool
    market_outcome: Optional[bool] = None


# Transaction schemas
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    action: str
    outcome: str
    shares: float
    price_per_share: float
    total_cost: float
    created_at: datetime

    class Config:
        from_attributes = True


# Leaderboard
class LeaderboardEntry(BaseModel):
    username: str
    balance: float
    rank: int
