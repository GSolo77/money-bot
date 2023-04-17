import asyncio
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters

from config import TELEGRAM_MANAGER_ID
from handlers.common import default_fallbacks
from handlers.keyboards import MAIN_KEYBOARD, CANCEL_KEYBOARD
from messages.common import QUESTION_PROMPT_MESSAGE, MainButtons, \
    QUESTION_SUCCESS_MESSAGE
from services.filters import TEXT_NOT_CMND_NOR_BTN
from services.utils import SLEEP_TIMEOUT

logger = logging.getLogger(__name__)
QUESTION = 0


async def question(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await asyncio.sleep(SLEEP_TIMEOUT)
    await update.message.reply_text(
        QUESTION_PROMPT_MESSAGE,
        reply_markup=CANCEL_KEYBOARD,
        parse_mode=ParseMode.MARKDOWN,
    )
    return QUESTION


async def user_question(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.forward(TELEGRAM_MANAGER_ID)
    await update.message.reply_text(
        QUESTION_SUCCESS_MESSAGE,
        reply_markup=MAIN_KEYBOARD,
    )
    context.user_data.clear()

    return ConversationHandler.END


question_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(MainButtons.question), question),
        CommandHandler('question', question),
    ],
    states={
        QUESTION: [MessageHandler(TEXT_NOT_CMND_NOR_BTN, user_question)],
    },
    fallbacks=default_fallbacks,
    map_to_parent={
        ConversationHandler.END: 'CHOOSING',
    },
    name="question_conv",
    persistent=True,
)
