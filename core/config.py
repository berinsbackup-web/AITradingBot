import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

TRADING_MODE = os.getenv('TRADING_MODE', 'paper').lower()

def is_live_mode():
    return TRADING_MODE == 'live'

@dataclass
class TradingConfig:
    UPSTOX_CLIENT_ID: str = os.getenv("UPSTOX_CLIENT_ID", "")
    UPSTOX_CLIENT_SECRET: str = os.getenv("UPSTOX_CLIENT_SECRET", "")
    UPSTOX_ACCESS_TOKEN: str = os.getenv("UPSTOX_ACCESS_TOKEN", "")
    UPSTOX_REDIRECT_URI: str = os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/callback")
    UPSTOX_ENV: str = os.getenv("UPSTOX_ENV", "sandbox")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    DB_USER: str = os.getenv("DB_USER", "trading_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "trading_bot")

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "")
    TO_EMAIL: str = os.getenv("TO_EMAIL", "")

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    BASE_CAPITAL: float = float(os.getenv("BASE_CAPITAL", "100000.0"))
    MAX_RISK_PER_TRADE: float = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))
    MAX_POSITIONS: int = int(os.getenv("MAX_POSITIONS", "10"))
    MAX_DAILY_DRAWDOWN: float = float(os.getenv("MAX_DAILY_DRAWDOWN", "0.05"))

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/trading_bot.log")

    @classmethod
    def refresh_access_token(cls, new_token: str):
        os.environ["UPSTOX_ACCESS_TOKEN"] = new_token
        cls.UPSTOX_ACCESS_TOKEN = new_token
        # Optionally, persist to a .env file or secure storage
