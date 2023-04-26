from itertools import permutations
from typing import Iterable

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import TELEGRAM_MANAGER_ID
from handlers.keyboards import build_inline_keyboard
from messages.common import ApprovalButtons

SLEEP_TIMEOUT = 0.5


def to_number(update: Update) -> tuple[float | None, bool]:
    """Check if `update.message.text` is convertable to `float`
    and return tuple of `float, False`. Otherwise return
    tuple `conv_step, True`.
    """
    try:
        return float(update.message.text), False
    except ValueError:
        return None, True


def user_request(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    return "\n".join(context.user_data[key].values())


def validate_unique_states(conversations: Iterable[ConversationHandler]):
    for conv1, conv2 in permutations(conversations, r=2):
        if set(conv1.states) & set(conv2.states):
            raise ValueError("Conversations could not share same state")


def init_user_data(context: ContextTypes.DEFAULT_TYPE, key: str) -> None:
    context.user_data.clear()
    context.user_data[key] = {}


async def send_user_request_to_manager(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        data_key: str,
) -> str:
    if update.callback_query.data != ApprovalButtons.approve.name:
        return "Отменено"

    user = update.effective_user
    user_final_request = (
        f"Заявка пользователя {user.last_name} {user.first_name} "
        f"(@{user.username}):\n\n"
    )
    user_final_request += user_request(context, data_key)
    await context.bot.send_message(
        TELEGRAM_MANAGER_ID,
        user_final_request,
        parse_mode=ParseMode.MARKDOWN,
    )
    return (
        "Ваша заявка успешно отправлена! "
        "В ближайшее время с вами свяжется наш менеджер"
    )


async def approve_user_request(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        data_key: str
) -> None:
    message = (
        f"Ваша заявка:\n\n{user_request(context, data_key)}\n\n"
        f"Подтвердить?"
    )
    await context.bot.send_message(
        update.effective_user.id,
        message,
        reply_markup=build_inline_keyboard(ApprovalButtons, rows=1),
    )
