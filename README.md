# Prediction Market

A full-stack prediction market application where users can create markets, trade Yes/No shares, and compete on a leaderboard.

## Features

- **Create Markets**: Ask questions about future events with resolution dates
- **Trade Shares**: Buy and sell Yes/No shares with dynamic pricing (LMSR)
- **Portfolio Tracking**: View your positions and their current value
- **Leaderboard**: Compete with other traders
- **Play Money**: Every user starts with $1,000
- **Telegram Token Gate**: NFT-gated private Telegram group for holders (see [backend/tokengate/README.md](backend/tokengate/README.md))

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React + Vite
- **Pricing Engine**: Logarithmic Market Scoring Rule (LMSR)

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python seed.py          # Optional: load sample data
uvicorn main:app --reload --port 8000
```

### Frontend (Development)

```bash
cd frontend
npm install
npm run dev
```

### Production (Single Server)

```bash
cd frontend && npm run build && cd ..
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend serves the built frontend automatically.

## API Docs

Visit `http://localhost:8000/docs` for the interactive API documentation.

## Demo Accounts

After running `seed.py`:
- **alice** / password123
- **bob** / password123
- **charlie** / password123
