import os
import random
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PREDICTIONS_FILE = "predictions.txt"

def load_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        logger.error(f"Файл {PREDICTIONS_FILE} не найден!")
        return ["Похоже, в печеньке ничего нет... 🍪"]
    try:
        with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
            predictions = [line.strip() for line in f if line.strip()]
        logger.info(f"Загружено {len(predictions)} предсказаний.")
        return predictions
    except Exception as e:
        logger.error(f"Ошибка при загрузке {PREDICTIONS_FILE}: {e}")
        return ["Ошибка загрузки предсказаний. Попробуй позже!"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍪 Добро пожаловать в Печеньку с Предсказаниями!\n\n"
        "Напиши /cookie, чтобы получить мудрость дня."
    )

async def cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    predictions = load_predictions()
    fortune = random.choice(predictions)
    await update.message.reply_text(f"🥠 {fortune}")

# Health-check эндпоинт для Render
async def health_check(request):
    return web.Response(text="OK", content_type="text/plain")

# Webhook-обработчик (не используется напрямую — его вызывает Telegram)
async def webhook_handler(request):
    # Тело запроса передаётся в Application
    pass

async def main():
    # Получаем настройки из переменных окружения
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("❌ Переменная BOT_TOKEN не установлена!")

    # Render задаёт PORT автоматически
    port = int(os.environ.get("PORT", "10000"))

    # Создаём приложение Telegram
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cookie", cookie))

    # Инициализируем aiohttp сервер
    app = web.Application()
    app.router.add_get("/", health_check)  # для Render health check
    app.router.add_post(f"/{token}", application.process_update)  # webhook от Telegram

    # Устанавливаем webhook у Telegram (один раз при старте)
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'your-bot.onrender.com')}/{token}"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Webhook установлен: {webhook_url}")

    # Запускаем веб-сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Сервер запущен на порту {port}")

    # Ожидаем завершения
    try:
        while True:
            await asyncio.sleep(3600)  # keep alive
    except KeyboardInterrupt:
        pass
    finally:
        await application.stop()

if __name__ == "__main__":
    asyncio.run(main())