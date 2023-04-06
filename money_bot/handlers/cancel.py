import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from handlers.keyboards import MAIN_KEYBOARD

logger = logging.getLogger(__name__)


async def cancel(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    logger.info("cancel called")
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=MAIN_KEYBOARD,
    )

    return ConversationHandler.END
