import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./predictionmarket.db")
JWT_SECRET = os.getenv("JWT_SECRET", "prediction-market-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
STARTING_BALANCE = 1000.0
DEFAULT_LIQUIDITY = 100.0
