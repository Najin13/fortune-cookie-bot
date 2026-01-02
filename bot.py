import os
import random
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PREDICTIONS_FILE = "predictions.txt"

def load_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        return ["Похоже, в печеньке ничего нет... 🍪"]
    try:
        with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return ["Ошибка загрузки предсказаний."]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍪 Добро пожаловать в Печеньку с Предсказаниями!\n\n"
        "Напиши /cookie, чтобы получить мудрость дня."
    )

async def cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    predictions = load_predictions()
    fortune = random.choice(predictions)
    await update.message.reply_text(f"🥠 {fortune}")

def main():
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cookie", cookie))
    logger.info("✅ Бот запускается в режиме polling...")
    app.run_polling()

if __name__ == "__main__":
    main()