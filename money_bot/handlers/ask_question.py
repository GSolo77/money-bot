import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters

from config import TELEGRAM_MANAGER_ID
from filters import ButtonsFilter
from handlers.cancel import cancel
from handlers.keyboards import MAIN_KEYBOARD
from messages.common import QUESTION_PROMPT_MESSAGE, MainButtons, \
    QUESTION_SUCCESS_MESSAGE

logger = logging.getLogger(__name__)
QUESTION = 0


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info('question. user_data %s', context.user_data)
    logger.info('question. call_back %s', update.callback_query)
    await update.message.reply_text(
        QUESTION_PROMPT_MESSAGE,
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN,
    )
    return QUESTION


async def user_question(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    # if message exists (text or photo) or user did not send button text –
    # do not forward to manager
    if (
        (update.message.text or update.message.photo)
        and not any(str(button) in update.message.text for button in MainButtons)
    ):
        await update.message.forward(TELEGRAM_MANAGER_ID)

    await update.message.reply_text(
        QUESTION_SUCCESS_MESSAGE,
        reply_markup=MAIN_KEYBOARD,
    )

    return ConversationHandler.END


question_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex(MainButtons.question), question),
        CommandHandler('question', question),
    ],
    states={
        QUESTION: [MessageHandler(~filters.COMMAND, user_question)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(ButtonsFilter(*MainButtons), cancel),
    ],
    allow_reentry=True,
    name='question_dialog',
    persistent=True,
)
