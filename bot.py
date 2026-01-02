import os
import random
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREDICTIONS_FILE = "predictions.txt"

def load_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        return ["Печенька пуста... 🍪"]
    try:
        with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return ["Ошибка загрузки."]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍪 Напиши /cookie!")

async def cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🥠 {random.choice(load_predictions())}")

async def health_check(request):
    return web.Response(text="OK")

async def main():
    token = os.environ["BOT_TOKEN"]
    port = int(os.environ.get("PORT", 10000))
    host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")

    # Создаём приложение
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cookie", cookie))

    # Webhook URL
    webhook_url = f"https://{host}/{token}"
    await app.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook установлен: {webhook_url}")

    # aiohttp сервер
    web_app = web.Application()
    web_app.router.add_get("/", health_check)
    web_app.router.add_post(f"/{token}", app.process_update)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Сервер запущен на порту {port}")

    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())