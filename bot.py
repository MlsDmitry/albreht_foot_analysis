
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

from main2 import bot_wants_diagnosis


API_TOKEN = '8114007451:AAG11QPMo7K6eBxrxcIb_sPHlrYb65XWpdc'

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, WANTS_DIAGNOSIS = range(3)

reply_keyboard = [
    ["Возраст"],["Пол"], ["Длина стопы"],
    ["Высота от пола до ладьевидной кости"],
    ["Ширина стопы на уровне пучков"], ["Высота от пола до бугристости ладьевидной кости"],
    ["Получить диагноз"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Здравствуйте! Это бот, который может помочь врачу в постановке диагноза плоскостопия. "
        "Для получения диагноза укажите данные пациента.",
        reply_markup=markup,
    )

    return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(f"Отлично! Можете указать {text.lower()} пациента в сообщении и отправить мне.")

    return TYPING_REPLY


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for a description of a custom category."""
    await update.message.reply_text(
        'Alright, please send me the category first, for example "Most impressive skill"'
    )

    return TYPING_CHOICE


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(
        "Прекрасно! На данный момент я знаю о пациенте следующую информацию:"
        f"{facts_to_str(user_data)}"
        ""
        "Вы можете дополнить ее или изменить при необходимости.",
        reply_markup=markup,
    )

    return CHOOSING

async def wants_diagnosis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    text = update.message.text

    diagnosis_text = bot_wants_diagnosis(user_data["Возраст"], user_data["Пол"], float(user_data["Длина стопы"]), float(user_data["Высота от пола до ладьевидной кости"]), float(user_data["Высота от пола до бугристости ладьевидной кости"]), float(user_data["Ширина стопы на уровне пучков"]))

    await update.message.reply_text(diagnosis_text,
                                    reply_markup=ReplyKeyboardRemove())

    return CHOOSING



async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(API_TOKEN).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex(f"^({'|'.join([text[0] for text in reply_keyboard[:-1]])})$"), regular_choice
                ),
                MessageHandler(filters.Regex(f"^{reply_keyboard[-1]}"), wants_diagnosis)
                # MessageHandler(filters.Regex("^Something else...$"), custom_choice),
            ],
            # WANTS_DIAGNOSIS: [
            #     MessageHandler
            # ]
            # TYPING_CHOICE: [
            #     MessageHandler(
            #         filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), regular_choice
            #     )
            # ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()