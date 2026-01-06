from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import Application

from src.services.ingest import ingest_product, get_last_price_delta
from src.services.subscriptions import list_all_active_subscriptions

def start_scheduler(app: Application, interval_seconds: int) -> None:
    scheduler = BackgroundScheduler()

    def job_wrapper():
        app.create_task(poll_and_notify(app))

    scheduler.add_job(job_wrapper, "interval", seconds=interval_seconds, max_instances=1)
    scheduler.start()

async def poll_and_notify(app: Application) -> None:
    subs = list_all_active_subscriptions()

    for chat_id, product_id, threshold in subs:
        try:
            ingest_product(product_id)
            delta = get_last_price_delta(product_id)

            cur = delta["current_price"]
            prev = delta["prev_price"]
            pct = delta["percent"]

            if cur is None or prev is None or pct is None:
                continue

            if abs(pct) >= threshold:
                sign = "+" if pct >= 0 else ""
                text = (
                    f"Товар {product_id}: изменение цены {sign}{pct:.2f}%.\n"
                    f"Порог: {threshold}%."
                )
                await app.bot.send_message(chat_id=chat_id, text=text)
        except Exception:
            continue
