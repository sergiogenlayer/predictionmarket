"""Seed the database with sample data for demo purposes."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
from models import User, Market, Position, Transaction
from auth import hash_password
from market_maker import cost_to_buy, price_yes

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed():
    # Check if already seeded
    if db.query(User).count() > 0:
        print("Database already has data, skipping seed.")
        return

    # Create users
    users = [
        User(username="alice", email="alice@example.com",
             password_hash=hash_password("password123"), balance=1000.0),
        User(username="bob", email="bob@example.com",
             password_hash=hash_password("password123"), balance=1000.0),
        User(username="charlie", email="charlie@example.com",
             password_hash=hash_password("password123"), balance=1000.0),
    ]
    for u in users:
        db.add(u)
    db.commit()
    for u in users:
        db.refresh(u)

    # Create markets
    markets_data = [
        {
            "title": "Will AI pass the Turing test convincingly by 2027?",
            "description": "Resolves YES if a widely recognized AI system passes a rigorous Turing test judged by a panel of experts before January 1, 2027.",
            "resolution_date": datetime(2027, 1, 1),
            "creator": users[0],
        },
        {
            "title": "Will humans land on Mars before 2030?",
            "description": "Resolves YES if a crewed mission successfully lands on the surface of Mars before January 1, 2030.",
            "resolution_date": datetime(2030, 1, 1),
            "creator": users[1],
        },
        {
            "title": "Will Bitcoin exceed $200,000 in 2026?",
            "description": "Resolves YES if Bitcoin's price exceeds $200,000 USD on any major exchange at any point during 2026.",
            "resolution_date": datetime(2026, 12, 31),
            "creator": users[0],
        },
        {
            "title": "Will a self-driving car service operate in 50+ US cities by 2027?",
            "description": "Resolves YES if any single autonomous vehicle service operates commercially in 50 or more US cities before January 1, 2027.",
            "resolution_date": datetime(2027, 1, 1),
            "creator": users[2],
        },
        {
            "title": "Will global temperatures exceed 1.5C above pre-industrial levels in 2026?",
            "description": "Resolves YES if the global average temperature in 2026 exceeds 1.5 degrees Celsius above pre-industrial levels according to NASA or NOAA.",
            "resolution_date": datetime(2027, 3, 1),
            "creator": users[1],
        },
    ]

    markets = []
    for md in markets_data:
        m = Market(
            title=md["title"],
            description=md["description"],
            creator_id=md["creator"].id,
            resolution_date=md["resolution_date"],
            liquidity_param=100.0,
            q_yes=0.0,
            q_no=0.0,
        )
        db.add(m)
        markets.append(m)
    db.commit()
    for m in markets:
        db.refresh(m)

    # Simulate some trades
    trades = [
        (users[0], markets[0], "yes", 20),
        (users[1], markets[0], "yes", 15),
        (users[2], markets[0], "no", 10),
        (users[1], markets[1], "no", 25),
        (users[0], markets[1], "yes", 10),
        (users[2], markets[2], "yes", 30),
        (users[0], markets[2], "no", 20),
        (users[1], markets[3], "yes", 15),
        (users[2], markets[4], "yes", 20),
        (users[0], markets[4], "no", 15),
    ]

    for user, market, outcome, shares in trades:
        b = market.liquidity_param
        cost = cost_to_buy(market.q_yes, market.q_no, b, outcome, shares)
        avg_price = cost / shares

        user.balance -= cost

        pos = db.query(Position).filter(
            Position.user_id == user.id,
            Position.market_id == market.id,
        ).first()
        if not pos:
            pos = Position(user_id=user.id, market_id=market.id)
            db.add(pos)
            db.flush()

        if outcome == "yes":
            pos.shares_yes += shares
            market.q_yes += shares
        else:
            pos.shares_no += shares
            market.q_no += shares

        txn = Transaction(
            user_id=user.id,
            market_id=market.id,
            action="buy",
            outcome=outcome,
            shares=shares,
            price_per_share=avg_price,
            total_cost=cost,
        )
        db.add(txn)

    db.commit()
    print("Database seeded successfully!")
    print(f"  Users: {db.query(User).count()}")
    print(f"  Markets: {db.query(Market).count()}")
    print(f"  Transactions: {db.query(Transaction).count()}")


if __name__ == "__main__":
    seed()
    db.close()
