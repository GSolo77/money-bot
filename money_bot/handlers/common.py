import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters

from config import TELEGRAM_DEVELOPER_ID
from handlers.keyboards import MAIN_KEYBOARD
from messages.common import START_MESSAGE, MainButtons

logger = logging.getLogger(__name__)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(START_MESSAGE, reply_markup=MAIN_KEYBOARD)
    return 'CHOOSING'


async def reply_to_others(update: Update,
                          _: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.sticker:
        text = "Классный стикер, сохранил!"
    elif update.message.video:
        text = "Интересное видео, видел его вчера!"
    elif update.message.photo:
        text = "Классная фотка!"
    elif update.message.text:
        text = "Такие сложные слова я не понимаю."
    else:
        text = "Что-то на эльфийском..."
    text = (
        f'{text}\n\nВоспользуйтесь лучше удобной клавиатурой команд.\n'
        'А если у вас возник какой-то вопрос нажмите '
        f'на кнопку «{MainButtons.question}» (/question).'
    )
    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Главное меню", reply_markup=MAIN_KEYBOARD)
    context.user_data.clear()

    return ConversationHandler.END


async def error_handler(update: object,
                        context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(
        msg="Exception while handling an update:", exc_info=context.error
    )

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    if isinstance(update, Update):
        update_str = update.to_dict()
    else:
        update_str = str(update)
    html_update_str = html.escape(
        json.dumps(update_str, indent=2, ensure_ascii=False)
    )
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html_update_str}"
        "</pre>\n\n<pre>"
        f"context.chat_data = {html.escape(str(context.chat_data))}</pre>"
        f"\n\n<pre>context.user_data = {html.escape(str(context.user_data))}"
        f"</pre>\n\n<pre>{html.escape(tb_string)}</pre>"
    )

    await context.bot.send_message(
        chat_id=TELEGRAM_DEVELOPER_ID, text=message, parse_mode=ParseMode.HTML
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Что-то пошло не так 🙁 Пожалуйста, попробуйте позже"
    )
    return ConversationHandler.END


default_fallbacks = [
    CommandHandler("cancel", cancel),
    MessageHandler(filters.Regex(MainButtons.back_to_menu), cancel)
]
