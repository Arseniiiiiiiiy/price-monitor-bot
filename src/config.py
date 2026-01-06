import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass(frozen=True)
class Settings:
    db_path: str
    simulate_price_change: bool
    bot_token: str
    poll_interval_seconds: int

def _must_get(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

settings = Settings(
    db_path=os.getenv("DB_PATH", "data.sqlite3"),
    simulate_price_change=os.getenv("SIMULATE_PRICE_CHANGE", "0") == "0",
    bot_token=_must_get("BOT_TOKEN"),
    poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "300")),
)
