import os
import random
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PREDICTIONS_FILE = "predictions.txt"
_cached_predictions = None

def load_predictions():
    global _cached_predictions
    if _cached_predictions is not None:
        return _cached_predictions

    if not os.path.exists(PREDICTIONS_FILE):
        logger.error(f"Файл {PREDICTIONS_FILE} не найден!")
        _cached_predictions = ["Похоже, в печеньке ничего нет... 🍪"]
        return _cached_predictions

    try:
        with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        logger.info(f"Загружено {len(lines)} предсказаний.")
        _cached_predictions = lines
        return lines
    except Exception as e:
        logger.error(f"Ошибка при загрузке {PREDICTIONS_FILE}: {e}")
        _cached_predictions = ["Ошибка загрузки предсказаний. Попробуй позже!"]
        return _cached_predictions

# Клавиатуры
MAIN_MENU = ReplyKeyboardMarkup(
    [["🥠 Случайное", "🔢 По номеру"]],
    resize_keyboard=True,
    one_time_keyboard=False
)

MORE_BUTTON = ReplyKeyboardMarkup(
    [["🔄 Ещё"]],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍪 Добро пожаловать в Печеньку с Предсказаниями!\n\n"
        "Выбери, как получить мудрость:",
        reply_markup=MAIN_MENU
    )

def get_random_fortune():
    predictions = load_predictions()
    return random.choice(predictions)

async def send_fortune(update: Update, fortune: str):
    """Отправляет предсказание с кнопкой «Ещё»"""
    await update.message.reply_text(
        f"🥠 {fortune}",
        reply_markup=MORE_BUTTON
    )

async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    predictions = load_predictions()
    total = len(predictions)

    # Обработка главного меню
    if text == "🥠 Случайное":
        fortune = get_random_fortune()
        await send_fortune(update, fortune)

    elif text == "🔢 По номеру":
        await update.message.reply_text(
            f"Введи номер предсказания (от 1 до {total}):"
        )
        context.user_data["awaiting_pick_number"] = True

    # Обработка кнопки «🔄 Ещё»
    elif text == "🔄 Ещё":
        fortune = get_random_fortune()
        await send_fortune(update, fortune)

    # Обработка ввода номера
    elif context.user_data.get("awaiting_pick_number"):
        context.user_data["awaiting_pick_number"] = False
        try:
            num = int(text.strip())
            if 1 <= num <= total:
                fortune = predictions[num - 1]
                await send_fortune(update, fortune)
            else:
                await update.message.reply_text(
                    f"Номер должен быть от 1 до {total}. Попробуй ещё раз:"
                )
                context.user_data["awaiting_pick_number"] = True
        except ValueError:
            await update.message.reply_text(
                "Пожалуйста, введи целое число. Попробуй ещё раз:"
            )
            context.user_data["awaiting_pick_number"] = True

    # Любое другое сообщение — возвращаем в меню
    else:
        await update.message.reply_text(
            "Используй кнопки ниже:",
            reply_markup=MAIN_MENU
        )

def main():
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_button))

    logger.info("✅ Бот запущен с кнопками и «🔄 Ещё»")
    app.run_polling()

if __name__ == "__main__":
    main()