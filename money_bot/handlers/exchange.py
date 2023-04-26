import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from handlers.common import default_fallbacks
from handlers.keyboards import MAIN_KEYBOARD, build_inline_keyboard, \
    CANCEL_KEYBOARD
from messages.common import ApprovalButtons, MainButtons, PayMethod, \
    AMOUNT_PROMPT
from messages.exchange import ExchangeType, ExchangeCurrency, \
    ExchangeNetwork, EXCHANGE_INFO_MESSAGE
from services.utils import to_number, SLEEP_TIMEOUT
from services.filters import TEXT_NOT_CMND_NOR_BTN
from services.manager import send_user_request_to_manager

logger = logging.getLogger(__name__)

USER_DATA_KEY = 'exchange_request'
TYPE, CURRENCY, PAY_METHOD, AMOUNT, NETWORK, APPROVE = range(1, 7)


async def exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[USER_DATA_KEY] = {}
    await asyncio.sleep(SLEEP_TIMEOUT)
    await update.message.reply_text(
        EXCHANGE_INFO_MESSAGE,
        reply_markup=CANCEL_KEYBOARD,
    )
    await update.message.reply_text(
        "Выберите тип операции",
        reply_markup=build_inline_keyboard(ExchangeType, rows=2),
    )

    return TYPE


async def exchange_type(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][TYPE] = (
        f"Тип операции: {ExchangeType.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_text(
        "Выберите валюту оплаты",
        reply_markup=build_inline_keyboard(ExchangeCurrency, rows=3),
    )

    return CURRENCY


async def exchange_currency(update: Update,
                            context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][CURRENCY] = (
        f"Валюта оплаты: {ExchangeCurrency.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_text(
        "Выберите способ оплаты",
        reply_markup=build_inline_keyboard(
            PayMethod,
            rows=3,
            exclude_names=[PayMethod.cash.name],
        ),
    )

    return PAY_METHOD


async def exchange_pay_method(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][PAY_METHOD] = (
        f"Способ оплаты: {PayMethod.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_text(
        "Выберите сеть",
        reply_markup=build_inline_keyboard(ExchangeNetwork, rows=2),
    )

    return NETWORK


async def exchange_network(update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][NETWORK] = (
        f"Сеть: {ExchangeNetwork.value_of(query.data)}"
    )
    await query.answer()
    await query.edit_message_reply_markup(None)
    await context.bot.send_message(
        query.message.chat_id,
        "Введите количество USDT в числовом формате",
    )
    return AMOUNT


async def exchange_amount(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    number, err = to_number(update)
    if err:
        await update.message.reply_text(AMOUNT_PROMPT)
        return AMOUNT

    context.user_data[USER_DATA_KEY][AMOUNT] = f"Кол-во USDT: {int(number)}"
    final_request = "\n".join(context.user_data[USER_DATA_KEY].values())
    await update.message.reply_text(
        f"Ваша заявка:\n\n{final_request}\n\nПодтвердить?",
        reply_markup=build_inline_keyboard(ApprovalButtons, rows=1),
    )

    return APPROVE


async def exchange_approve(update: Update,
                           context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.edit_reply_markup(None)

    await query.message.reply_text(
        await send_user_request_to_manager(update, context, USER_DATA_KEY),
        reply_markup=MAIN_KEYBOARD,
    )
    context.user_data.clear()

    return ConversationHandler.END


exchange_conv = ConversationHandler(
    entry_points=[
        CommandHandler("exchange", exchange),
        MessageHandler(filters.Regex(MainButtons.exchange), exchange),
    ],
    states={
        TYPE: [CallbackQueryHandler(exchange_type)],
        CURRENCY: [CallbackQueryHandler(exchange_currency)],
        PAY_METHOD: [CallbackQueryHandler(exchange_pay_method)],
        NETWORK: [CallbackQueryHandler(exchange_network)],
        AMOUNT: [MessageHandler(TEXT_NOT_CMND_NOR_BTN, exchange_amount)],
        APPROVE: [CallbackQueryHandler(exchange_approve)],
    },
    fallbacks=default_fallbacks,
    map_to_parent={
        ConversationHandler.END: 'CHOOSING',
    },
    allow_reentry=True,
    name=USER_DATA_KEY,
    persistent=True,
)
