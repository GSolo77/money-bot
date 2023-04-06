import logging

from config import TELEGRAM_BOT_TOKEN

from telegram.ext import Application, PicklePersistence, CommandHandler

from handlers.ask_question import question_conv
from handlers.exchange import exchange_conv
from handlers.russian_transfer import russian_transfer_conv
from handlers.start import start

logger = logging.getLogger(__name__)


def main() -> None:
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(
        TELEGRAM_BOT_TOKEN,
    ).persistence(
        persistence,
    ).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(question_conv)
    application.add_handler(exchange_conv)
    application.add_handler(russian_transfer_conv)
    application.run_polling()


if __name__ == "__main__":
    main()
