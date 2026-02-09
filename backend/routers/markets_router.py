from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Market, Position, Transaction
from schemas import (
    MarketCreate, MarketResponse, TradeRequest, TradeResponse,
    ResolveRequest, TransactionResponse
)
from auth import get_current_user, get_optional_user
from market_maker import price_yes, price_no, cost_to_buy, cost_to_sell

router = APIRouter(prefix="/api/markets", tags=["markets"])


def market_to_response(market: Market, volume: float = None) -> MarketResponse:
    return MarketResponse(
        id=market.id,
        title=market.title,
        description=market.description,
        creator_id=market.creator_id,
        creator_username=market.creator.username if market.creator else None,
        created_at=market.created_at,
        resolution_date=market.resolution_date,
        resolved=market.resolved,
        outcome=market.outcome,
        price_yes=price_yes(market.q_yes, market.q_no, market.liquidity_param),
        price_no=price_no(market.q_yes, market.q_no, market.liquidity_param),
        q_yes=market.q_yes,
        q_no=market.q_no,
        liquidity_param=market.liquidity_param,
        total_volume=volume,
    )


@router.get("/", response_model=list[MarketResponse])
def list_markets(
    search: str = Query(default="", max_length=200),
    status: str = Query(default="all", pattern="^(all|active|resolved)$"),
    db: Session = Depends(get_db),
):
    query = db.query(Market)

    if search:
        query = query.filter(Market.title.ilike(f"%{search}%"))
    if status == "active":
        query = query.filter(Market.resolved == False)
    elif status == "resolved":
        query = query.filter(Market.resolved == True)

    markets = query.order_by(Market.created_at.desc()).all()

    # Get volumes
    volumes = dict(
        db.query(Transaction.market_id, func.sum(func.abs(Transaction.total_cost)))
        .group_by(Transaction.market_id)
        .all()
    )

    return [market_to_response(m, volumes.get(m.id, 0)) for m in markets]


@router.post("/", response_model=MarketResponse)
def create_market(
    data: MarketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.resolution_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Resolution date must be in the future")

    market = Market(
        title=data.title,
        description=data.description,
        creator_id=current_user.id,
        resolution_date=data.resolution_date,
        liquidity_param=data.liquidity_param,
        q_yes=0.0,
        q_no=0.0,
    )
    db.add(market)
    db.commit()
    db.refresh(market)

    return market_to_response(market, 0)


@router.get("/{market_id}", response_model=MarketResponse)
def get_market(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    volume = (
        db.query(func.sum(func.abs(Transaction.total_cost)))
        .filter(Transaction.market_id == market_id)
        .scalar() or 0
    )

    return market_to_response(market, volume)


@router.post("/{market_id}/trade", response_model=TradeResponse)
def trade(
    market_id: int,
    data: TradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    if market.resolved:
        raise HTTPException(status_code=400, detail="Market is already resolved")
    if market.resolution_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Market has passed its resolution date")

    # Get or create position
    position = (
        db.query(Position)
        .filter(Position.user_id == current_user.id, Position.market_id == market_id)
        .first()
    )
    if not position:
        position = Position(user_id=current_user.id, market_id=market_id)
        db.add(position)
        db.flush()

    b = market.liquidity_param

    if data.action == "buy":
        cost = cost_to_buy(market.q_yes, market.q_no, b, data.outcome, data.shares)
        if cost > current_user.balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Cost: ${cost:.2f}, Balance: ${current_user.balance:.2f}"
            )

        current_user.balance -= cost
        if data.outcome == "yes":
            position.shares_yes += data.shares
            market.q_yes += data.shares
        else:
            position.shares_no += data.shares
            market.q_no += data.shares

        avg_price = cost / data.shares

    else:  # sell
        if data.outcome == "yes" and position.shares_yes < data.shares:
            raise HTTPException(status_code=400, detail="Not enough YES shares to sell")
        if data.outcome == "no" and position.shares_no < data.shares:
            raise HTTPException(status_code=400, detail="Not enough NO shares to sell")

        proceeds = cost_to_sell(market.q_yes, market.q_no, b, data.outcome, data.shares)
        current_user.balance += proceeds

        if data.outcome == "yes":
            position.shares_yes -= data.shares
            market.q_yes -= data.shares
        else:
            position.shares_no -= data.shares
            market.q_no -= data.shares

        cost = -proceeds
        avg_price = proceeds / data.shares

    # Record transaction
    txn = Transaction(
        user_id=current_user.id,
        market_id=market_id,
        action=data.action,
        outcome=data.outcome,
        shares=data.shares,
        price_per_share=avg_price,
        total_cost=cost,
    )
    db.add(txn)
    db.commit()

    new_p_yes = price_yes(market.q_yes, market.q_no, b)
    new_p_no = price_no(market.q_yes, market.q_no, b)

    action_word = "Bought" if data.action == "buy" else "Sold"
    cost_word = "Cost" if data.action == "buy" else "Proceeds"
    amount = abs(cost)

    return TradeResponse(
        message=f"{action_word} {data.shares:.1f} {data.outcome.upper()} shares. {cost_word}: ${amount:.2f}",
        cost=cost,
        new_balance=current_user.balance,
        price_yes=new_p_yes,
        price_no=new_p_no,
        position_yes=position.shares_yes,
        position_no=position.shares_no,
    )


@router.post("/{market_id}/resolve", response_model=MarketResponse)
def resolve_market(
    market_id: int,
    data: ResolveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    if market.resolved:
        raise HTTPException(status_code=400, detail="Market is already resolved")
    if market.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the market creator can resolve it")

    market.resolved = True
    market.outcome = data.outcome

    # Pay out winners
    positions = db.query(Position).filter(Position.market_id == market_id).all()
    for pos in positions:
        payout = 0.0
        if data.outcome and pos.shares_yes > 0:
            payout += pos.shares_yes * 1.0  # YES wins: $1 per share
        if not data.outcome and pos.shares_no > 0:
            payout += pos.shares_no * 1.0  # NO wins: $1 per share

        if payout > 0:
            user = db.query(User).filter(User.id == pos.user_id).first()
            if user:
                user.balance += payout

    db.commit()
    db.refresh(market)

    volume = (
        db.query(func.sum(func.abs(Transaction.total_cost)))
        .filter(Transaction.market_id == market_id)
        .scalar() or 0
    )

    return market_to_response(market, volume)


@router.get("/{market_id}/transactions", response_model=list[TransactionResponse])
def get_transactions(market_id: int, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    txns = (
        db.query(Transaction)
        .filter(Transaction.market_id == market_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    result = []
    for t in txns:
        resp = TransactionResponse.model_validate(t)
        resp.username = t.user.username if t.user else None
        result.append(resp)

    return result
