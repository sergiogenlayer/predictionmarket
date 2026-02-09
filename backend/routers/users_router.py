from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Position, Market
from schemas import PositionResponse, LeaderboardEntry
from auth import get_current_user
from market_maker import price_yes, price_no

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me/positions", response_model=list[PositionResponse])
def get_my_positions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    positions = (
        db.query(Position)
        .filter(Position.user_id == current_user.id)
        .filter((Position.shares_yes > 0.001) | (Position.shares_no > 0.001))
        .all()
    )

    result = []
    for pos in positions:
        market = pos.market
        p_yes = price_yes(market.q_yes, market.q_no, market.liquidity_param)
        p_no = price_no(market.q_yes, market.q_no, market.liquidity_param)

        result.append(PositionResponse(
            market_id=market.id,
            market_title=market.title,
            shares_yes=pos.shares_yes,
            shares_no=pos.shares_no,
            current_price_yes=p_yes,
            current_price_no=p_no,
            market_resolved=market.resolved,
            market_outcome=market.outcome,
        ))

    return result


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.balance.desc()).limit(20).all()
    return [
        LeaderboardEntry(username=u.username, balance=u.balance, rank=i + 1)
        for i, u in enumerate(users)
    ]
