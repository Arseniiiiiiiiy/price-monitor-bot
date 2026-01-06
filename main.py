from src.db.sqlite import init_db
from src.config import settings
from src.bot.handlers import build_application
from src.scheduler import start_scheduler

def main() -> None:
    init_db()
    app = build_application(settings.bot_token)

    start_scheduler(app, settings.poll_interval_seconds)

    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()
