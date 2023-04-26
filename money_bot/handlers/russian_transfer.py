import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from handlers.common import default_fallbacks
from handlers.keyboards import MAIN_KEYBOARD, build_inline_keyboard, \
    CANCEL_KEYBOARD
from messages.common import MainButtons, PayMethod, AMOUNT_PROMPT
from messages.transfer import RUSSIAN_TRANSFER_MESSAGE, ReceiveMethod
from services.filters import TEXT_NOT_CMND_NOR_BTN
from services.utils import to_number, SLEEP_TIMEOUT, init_user_data, \
    approve_user_request, send_user_request_to_manager

logger = logging.getLogger(__name__)

USER_DATA_KEY = 'russian_transfer'
AMOUNT = 'RUSSIAN_AMOUNT'
ORIGIN = 'RUSSIAN_ORIGIN'
DESTINATION = 'RUSSIAN_DESTINATION'
PAY_METHOD = 'RUSSIAN_PAY_METHOD'
RECEIVE_METHOD = 'RUSSIAN_RECEIVE_METHOD'
APPROVE = 'RUSSIAN_APPROVE'


async def russian_transfer(update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> str:
    init_user_data(context, USER_DATA_KEY)
    await asyncio.sleep(SLEEP_TIMEOUT)
    await update.message.reply_text(
        RUSSIAN_TRANSFER_MESSAGE,
        reply_markup=CANCEL_KEYBOARD,
    )
    await update.message.reply_text(AMOUNT_PROMPT)

    return AMOUNT


async def russian_amount(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> str:
    number, err = to_number(update)
    if err:
        await update.message.reply_text(AMOUNT_PROMPT)
        return AMOUNT

    context.user_data[USER_DATA_KEY]['OP'] = (
        f"Тип операции: {MainButtons.russian_transfer}"
    )
    context.user_data[USER_DATA_KEY][AMOUNT] = f"Сумма: {number:.2f} ₽"
    await update.message.reply_text("Введите город отправления")

    return ORIGIN


async def russian_origin(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[USER_DATA_KEY][ORIGIN] = (
        f"Город отправления: {update.message.text.strip().capitalize()}"
    )

    exclude_names = [PayMethod.cash_minsk.name]
    if context.user_data[USER_DATA_KEY][ORIGIN] != "Москва":
        exclude_names.append(PayMethod.cash_moscow.name)

    await update.message.reply_text(
        "Выберите способ оплаты",
        reply_markup=build_inline_keyboard(
            PayMethod,
            rows=2,
            exclude_names=exclude_names,
        ),
    )

    return PAY_METHOD


async def russian_pay_method(update: Update,
                             context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][PAY_METHOD] = (
        f"Способ оплаты: {PayMethod.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_text("Введите город получения")

    return DESTINATION


async def russian_destination(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[USER_DATA_KEY][DESTINATION] = (
        f"Город получения: {update.message.text.strip().capitalize()}"
    )

    await update.message.reply_text(
        "Предпочтительный способ получения",
        reply_markup=build_inline_keyboard(ReceiveMethod, rows=2),
    )

    return RECEIVE_METHOD


async def russian_receive_method(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][RECEIVE_METHOD] = (
        f"Способ получения: {ReceiveMethod.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_reply_markup(None)
    await approve_user_request(update, context, USER_DATA_KEY)

    return APPROVE


async def russian_approve(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query

    await query.answer()
    await query.message.reply_text(
        await send_user_request_to_manager(update, context, USER_DATA_KEY),
        reply_markup=MAIN_KEYBOARD,
    )
    context.user_data.clear()

    return ConversationHandler.END


russian_transfer_conv = ConversationHandler(
    entry_points=[
        CommandHandler("russian_transfer", russian_transfer),
        MessageHandler(
            filters.Regex(MainButtons.russian_transfer), russian_transfer,
        ),
    ],
    states={
        AMOUNT: [MessageHandler(TEXT_NOT_CMND_NOR_BTN, russian_amount)],
        ORIGIN: [MessageHandler(TEXT_NOT_CMND_NOR_BTN, russian_origin)],
        DESTINATION: [
            MessageHandler(TEXT_NOT_CMND_NOR_BTN, russian_destination),
        ],
        PAY_METHOD: [CallbackQueryHandler(russian_pay_method)],
        RECEIVE_METHOD: [CallbackQueryHandler(russian_receive_method)],
        APPROVE: [CallbackQueryHandler(russian_approve)],
    },
    fallbacks=default_fallbacks,
    map_to_parent={
        ConversationHandler.END: 'CHOOSING',
    },
    allow_reentry=True,
    name=USER_DATA_KEY,
    persistent=True,
)
