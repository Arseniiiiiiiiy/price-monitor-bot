from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.services.ingest import ingest_product, get_last_price_delta
from src.db.sqlite import init_db

from src.services.subscriptions import (
    get_chat_default_threshold, set_chat_default_threshold,
    upsert_subscription, disable_subscription, list_active_subscriptions
)

import logging
logger = logging.getLogger("price_monitor")


def _fmt_money(x: float) -> str:
    return f"{x:.2f}"

async def set_threshold_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if not context.args:
        cur = get_chat_default_threshold(chat_id)
        await update.message.reply_text(f"Текущий порог: {cur}%. Пример: /set_threshold 5")
        return
    try:
        th = float(context.args[0])
        if th <= 0 or th > 100:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Нужен порог от 0 до 100. Пример: /set_threshold 5")
        return
    set_chat_default_threshold(chat_id, th)
    await update.message.reply_text(f"Ок. Новый дефолтный порог: {th}%.")

async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Команда /track. user_id=%s args=%s", update.effective_user.id, context.args)

    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Пример: /track 1 2 3")
        return
    default_th = get_chat_default_threshold(chat_id)
    added = 0
    for a in context.args:
        try:
            pid = int(a)
        except ValueError:
            continue
        upsert_subscription(chat_id, pid, default_th)
        added += 1
    await update.message.reply_text(f"Готово. Подписок добавлено: {added}. Проверь /list.")

async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Пример: /untrack 2")
        return
    try:
        pid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Нужен числовой id товара.")
        return
    disable_subscription(chat_id, pid)
    await update.message.reply_text("Ок. Отписал.")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    subs = list_active_subscriptions(chat_id)
    if not subs:
        await update.message.reply_text("Подписок нет. Добавь через /track 1 2 3")
        return
    lines = [f"{pid} (порог {th}%)" for pid, th in subs]
    await update.message.reply_text("Подписки:\n" + "\n".join(lines))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет. Я бот для мониторинга цен.\n"
        "Команды:\n"
        "/price <id> – обновить цену товара и показать изменение.\n"
        "Пример: /price 1."
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    logger.info("Команда /update. user_id=%s", update.effective_user.id)

    if not context.args:
        await update.message.reply_text("Пример: /price 1.")
        return

    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Нужен числовой id. Пример: /price 1.")
        return

    init_db()

    info = ingest_product(product_id)
    delta = get_last_price_delta(product_id)

    title = info["title"]
    cur = delta["current_price"]
    prev = delta["prev_price"]

    if cur is None:
        await update.message.reply_text("Нет данных по этому товару.")
        return

    if prev is None:
        text = (
            f"{product_id}: {title}\n"
            f"Цена: {_fmt_money(cur)} USD\n"
            f"Это первая запись, сравнивать пока не с чем."
        )
        await update.message.reply_text(text)
        return

    diff = delta["diff"]
    pct = delta["percent"]

    sign = "+" if diff >= 0 else ""
    text = (
        f"{product_id}: {title}\n"
        f"Было: {_fmt_money(prev)} USD\n"
        f"Стало: {_fmt_money(cur)} USD\n"
        f"Изменение: {sign}{_fmt_money(diff)} USD ({sign}{pct:.2f}%)."
    )
    await update.message.reply_text(text)

def build_application(bot_token: str) -> Application:
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("set_threshold", set_threshold_cmd))
    app.add_handler(CommandHandler("track", track))
    app.add_handler(CommandHandler("untrack", untrack))
    app.add_handler(CommandHandler("list", list_cmd))
    return app
