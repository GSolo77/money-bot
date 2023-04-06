from telegram import Update
from telegram.ext import ContextTypes

from handlers.keyboards import MAIN_KEYBOARD
from messages.common import START_MESSAGE


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(START_MESSAGE, reply_markup=MAIN_KEYBOARD)
