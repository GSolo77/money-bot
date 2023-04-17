from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import TELEGRAM_MANAGER_ID
from messages.common import ApprovalButtons
from services.utils import user_request


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
    return "Ваша заявка успешно отправлена!"
