import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from filters import ButtonsFilter
from handlers.cancel import cancel
from handlers.keyboards import MAIN_KEYBOARD, PAY_METHOD_KEYBOARD, \
    RECEIVE_METHOD_KEYBOARD, APPROVE_KEYBOARD
from messages.common import MainButtons, PayMethod, ApprovalButtons
from messages.transfer import RUSSIAN_TRANSFER_MESSAGE, ReceiveMethod

logger = logging.getLogger(__name__)
USER_DATA_KEY = 'russian_transfer'
AMOUNT, ORIGIN, DESTINATION, PAY_METHOD, RECEIVE_METHOD, APPROVE = 8, 9, 10, 11, 12, 13
STEPS_CALLBACK_MAPPING = {
    AMOUNT: None,
    ORIGIN: None,
    DESTINATION: None,
    PAY_METHOD: PayMethod,
    RECEIVE_METHOD: ReceiveMethod,
}


def build_transfer_message(user_data: dict) -> str:
    pass


async def russian_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(RUSSIAN_TRANSFER_MESSAGE, reply_markup=None)
    await update.message.reply_text("Введите сумму в числовом формате")

    return AMOUNT


async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        number = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Введите сумму в числовом формате")
        return AMOUNT

    context.user_data[USER_DATA_KEY] = {}
    context.user_data[USER_DATA_KEY][AMOUNT] = number
    await update.message.reply_text("Введите город отправления")

    return ORIGIN


async def origin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[USER_DATA_KEY][ORIGIN] = update.message.text
    await update.message.reply_text("Введите город получения")

    return DESTINATION


async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[USER_DATA_KEY][DESTINATION] = update.message.text
    await update.message.reply_text("Выберите способ оплаты", reply_markup=PAY_METHOD_KEYBOARD)

    return PAY_METHOD


async def pay_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][PAY_METHOD] = PayMethod.value_of(query.data)
    await query.answer()
    await query.edit_message_text("Предпочтительный способ получения", reply_markup=RECEIVE_METHOD_KEYBOARD)

    return RECEIVE_METHOD


async def receive_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][RECEIVE_METHOD] = ReceiveMethod.value_of(query.data)
    await query.answer()
    await query.edit_message_text(
        f"Ваша заявка:\n{context.user_data[USER_DATA_KEY]}\nПодтвердить?",
        reply_markup=APPROVE_KEYBOARD,
    )

    return APPROVE


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    if query.data == ApprovalButtons.approve.name:
        text = "Ваша заявка успешно отправлена!"
    else:
        text = "Отменено"

    await query.answer()
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text(text, reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END


russian_transfer_conv = ConversationHandler(
    entry_points=[
        CommandHandler("russian_transfer", russian_transfer),
        MessageHandler(filters.Regex(MainButtons.russian_transfer), russian_transfer),
    ],
    states={
        AMOUNT: [MessageHandler(filters.TEXT, amount)],
        ORIGIN: [MessageHandler(filters.TEXT, origin)],
        DESTINATION: [MessageHandler(filters.TEXT, destination)],
        PAY_METHOD: [CallbackQueryHandler(pay_method)],
        RECEIVE_METHOD: [CallbackQueryHandler(receive_method)],
        APPROVE: [CallbackQueryHandler(approve)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(ButtonsFilter(*MainButtons), cancel)
    ],
    allow_reentry=True,
    name='russian_transfer_dialog',
    persistent=True,
)
