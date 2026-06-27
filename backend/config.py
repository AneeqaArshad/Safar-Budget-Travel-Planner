from datetime import timedelta
import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY"
    )

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///travel_planner.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ANTHROPIC_API_KEY = os.getenv(
        "ANTHROPIC_API_KEY"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # ── Planning Constants ─────────────────

    MAX_HOURS_PER_DAY = 10
    MIN_ACTIVITY_GAP = 30
    DEFAULT_TRANSPORT_COST = 500
    DEFAULT_MEAL_COST = 1200