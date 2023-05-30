import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from handlers.common import default_fallbacks
from handlers.keyboards import build_inline_keyboard, MAIN_KEYBOARD, \
    CANCEL_KEYBOARD
from messages.common import MainButtons, PayMethod
from messages.transfer import ReceiveMethod, ABROAD_TRANSFER_MESSAGE, \
    OriginCurrency, RecipientType
from services.filters import TEXT_NOT_CMND_NOR_BTN
from services.utils import to_number, SLEEP_TIMEOUT, init_user_data, \
    approve_user_request, send_user_request_to_manager

logger = logging.getLogger(__name__)
USER_DATA_KEY = 'abroad_transfer'

ORIGIN_CURRENCY = 'ABROAD_ORIGIN_CURRENCY'
ORIGIN_INPUT_CURRENCY = 'ABROAD_ORIGIN_INPUT_CURRENCY'
DESTINATION_CURRENCY = 'ABROAD_DESTINATION_CURRENCY'
RECIPIENT_TYPE = 'ABROAD_RECIPIENT_TYPE'
ORIGIN = 'ABROAD_ORIGIN'
PAY_METHOD = 'ABROAD_PAY_METHOD'
RECEIVE_METHOD = 'ABROAD_RECEIVE_METHOD'
AMOUNT = 'ABROAD_AMOUNT'
DESTINATION_CITY = 'ABROAD_DESTINATION_CITY'
APPROVE = 'ABROAD_APPROVE'


async def abroad_transfer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    init_user_data(context, USER_DATA_KEY)
    await asyncio.sleep(SLEEP_TIMEOUT)
    await update.message.reply_text(
        ABROAD_TRANSFER_MESSAGE,
        reply_markup=CANCEL_KEYBOARD,
    )
    await update.message.reply_text(
        "Выберите валюту отправления",
        reply_markup=build_inline_keyboard(
            OriginCurrency,
            rows=4,
            exclude_names=[OriginCurrency.local.name],
        ),
    )
    return ORIGIN_CURRENCY


async def abroad_origin_cur(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY]['OP'] = (
        f"Тип операции: {MainButtons.abroad_transfer}"
    )
    await query.answer()

    if query.data == OriginCurrency.other.name:
        await query.edit_message_text("Введите валюту")
        return ORIGIN_INPUT_CURRENCY

    context.user_data[USER_DATA_KEY][ORIGIN_CURRENCY] = (
        f"Валюта отправления: {OriginCurrency.value_of(query.data)}"
    )
    await query.edit_message_text(
        "Выберите валюту получателя",
        reply_markup=build_inline_keyboard(
            OriginCurrency,
            rows=3,
            include_names=[
                OriginCurrency.usd.name,
                OriginCurrency.eur.name,
                OriginCurrency.rub.name,
                OriginCurrency.cny.name,
                OriginCurrency.local.name,
            ]
        ),
    )

    return DESTINATION_CURRENCY


async def abroad_origin_input_cur(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    context.user_data[USER_DATA_KEY][ORIGIN_CURRENCY] = (
        f"Валюта отправления: {update.message.text.strip()}"
    )
    await update.message.reply_text(
        "Выберите валюту получателя",
        reply_markup=build_inline_keyboard(
            OriginCurrency,
            rows=3,
            include_names=[
                OriginCurrency.usd.name,
                OriginCurrency.eur.name,
                OriginCurrency.rub.name,
                OriginCurrency.cny.name,
                OriginCurrency.local.name,
            ],
        ),
    )

    return DESTINATION_CURRENCY


async def abroad_destination_cur(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    currency = OriginCurrency.value_of(query.data)
    context.user_data[USER_DATA_KEY][DESTINATION_CURRENCY] = (
        f"Валюта получателя: {currency}"
    )
    await query.answer()
    await query.edit_message_text(
        f"Введите сумму в валюте получателя ({currency})"
    )
    return AMOUNT


async def abroad_amount(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> str:
    number, err = to_number(update)
    if err:
        await update.message.reply_text(
            "Пожалуйста, введите сумму в числовом формате"
        )
        return AMOUNT

    context.user_data[USER_DATA_KEY][AMOUNT] = f"Сумма: {number:.2f}"
    await update.message.reply_text(
        "Выберите способ оплаты",
        reply_markup=build_inline_keyboard(
            PayMethod,
            rows=2,
            include_names=[PayMethod.cash.name, PayMethod.bank.name],
        )
    )
    return PAY_METHOD


async def abroad_pay_method(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][PAY_METHOD] = (
        f"Способ оплаты: {PayMethod.value_of(query.data)}"
    )
    await query.answer()

    if query.data == PayMethod.cash.name:
        await query.edit_message_text("Введите город отправления")
    else:
        await query.edit_message_text("Введите название банка отправления")

    return ORIGIN


async def origin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if PayMethod.cash.value in context.user_data[USER_DATA_KEY][PAY_METHOD]:
        prompt = "Город отправления"
    else:
        prompt = "Банк отправления"

    context.user_data[USER_DATA_KEY][ORIGIN] = (
        f"{prompt}: {update.message.text.strip().capitalize()}"
    )
    await update.message.reply_text(
        "Выберите предпочтительный способ получения",
        reply_markup=build_inline_keyboard(ReceiveMethod, rows=2),
    )

    return RECEIVE_METHOD


async def abroad_receive_method(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][RECEIVE_METHOD] = (
        f"Способ получения: {ReceiveMethod.value_of(query.data)}"
    )
    await query.answer()

    if query.data == ReceiveMethod.cash.name:
        await query.edit_message_text("Введите город получения")
        return DESTINATION_CITY

    await query.edit_message_text(
        "Выберите тип получателя",
        reply_markup=build_inline_keyboard(RecipientType, rows=1),
    )
    return RECIPIENT_TYPE


async def abroad_destination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    context.user_data[USER_DATA_KEY][DESTINATION_CITY] = (
        f"Город получателя: {update.message.text.strip().capitalize()}"
    )

    await approve_user_request(update, context, USER_DATA_KEY)
    return APPROVE


async def abroad_recipient_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][RECIPIENT_TYPE] = (
        f"Тип получателя: {RecipientType.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_reply_markup(None)
    await approve_user_request(update, context, USER_DATA_KEY)

    return APPROVE


async def abroad_approve(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query

    await query.answer()
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.reply_text(
        await send_user_request_to_manager(update, context, USER_DATA_KEY),
        reply_markup=MAIN_KEYBOARD,
    )
    context.user_data.clear()

    return ConversationHandler.END


abroad_transfer_conv = ConversationHandler(
    entry_points=[
        CommandHandler("abroad_transfer", abroad_transfer),
        MessageHandler(
            filters.Regex(MainButtons.abroad_transfer),
            abroad_transfer,
        ),
    ],
    states={
        ORIGIN_CURRENCY: [CallbackQueryHandler(abroad_origin_cur)],
        ORIGIN_INPUT_CURRENCY: [
            MessageHandler(TEXT_NOT_CMND_NOR_BTN, abroad_origin_input_cur),
        ],
        DESTINATION_CURRENCY: [CallbackQueryHandler(abroad_destination_cur)],
        RECIPIENT_TYPE: [CallbackQueryHandler(abroad_recipient_type)],
        ORIGIN: [MessageHandler(TEXT_NOT_CMND_NOR_BTN, origin)],
        PAY_METHOD: [CallbackQueryHandler(abroad_pay_method)],
        RECEIVE_METHOD: [CallbackQueryHandler(abroad_receive_method)],
        AMOUNT: [MessageHandler(TEXT_NOT_CMND_NOR_BTN, abroad_amount)],
        DESTINATION_CITY: [
            MessageHandler(TEXT_NOT_CMND_NOR_BTN, abroad_destination),
        ],
        APPROVE: [CallbackQueryHandler(abroad_approve)],
    },
    fallbacks=default_fallbacks,
    map_to_parent={
        ConversationHandler.END: 'CHOOSING',
    },
    allow_reentry=True,
    name=USER_DATA_KEY,
    persistent=True,
)
