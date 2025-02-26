import asyncio
import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from handlers.common import default_fallbacks, MAIN_ENTRY_POINT
from handlers.keyboards import MAIN_KEYBOARD, build_inline_keyboard, \
    CANCEL_KEYBOARD
from messages.common import MainButtons, PayMethod
from messages.exchange import ExchangeType, ExchangeCurrency, \
    ExchangeNetwork, EXCHANGE_INFO_MESSAGE, ExchangeCrypto
from services.utils import SLEEP_TIMEOUT, init_user_data, \
    approve_user_request, send_user_request_to_manager

logger = logging.getLogger(__name__)

USER_DATA_KEY = 'exchange_request'
TYPE = 'EXCHANGE_TYPE'
NETWORK = 'EXCHANGE_NETWORK'
APPROVE = 'EXCHANGE_APPROVE'
GIVE = 'EXCHANGE_GIVE'
RECEIVE = 'EXCHANGE_RECEIVE'
RUB_METHOD = 'EXCHANGE_RUB_METHOD'


def _giveaway_keyboard(query_data: str) -> InlineKeyboardMarkup:
    if query_data == ExchangeType.sell.name:
        return build_inline_keyboard(ExchangeCrypto, rows=3)
    return build_inline_keyboard(ExchangeCurrency, rows=2)


def _receive_keyboard(query_data: str) -> InlineKeyboardMarkup:
    if query_data == ExchangeType.sell.name:
        return build_inline_keyboard(ExchangeCurrency, rows=2)
    return build_inline_keyboard(ExchangeCrypto, rows=3)


def _is_sell(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.chat_data[USER_DATA_KEY][TYPE] == ExchangeType.sell.name


async def exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    init_user_data(context, USER_DATA_KEY)

    await asyncio.sleep(SLEEP_TIMEOUT)
    await update.message.reply_text(
        EXCHANGE_INFO_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=CANCEL_KEYBOARD,
    )
    await update.message.reply_text(
        "Выберите тип операции",
        reply_markup=build_inline_keyboard(ExchangeType, rows=2),
    )

    return TYPE


async def exchange_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    context.user_data[USER_DATA_KEY]['OP'] = (
        f"Услуга: {MainButtons.exchange.value}"
    )
    context.user_data[USER_DATA_KEY][TYPE] = (
        f"Тип операции: {ExchangeType.value_of(query.data)}"
    )
    context.chat_data.setdefault(USER_DATA_KEY, {})[TYPE] = query.data
    await query.answer()
    await query.edit_message_text(
        "Отдаете",
        reply_markup=_giveaway_keyboard(query.data),
    )

    return GIVE


async def give(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    await query.answer()

    if _is_sell(context):
        # crypto was chosen
        context.user_data[USER_DATA_KEY][GIVE] = (
            f"Отдаете: {ExchangeCrypto.value_of(query.data)}"
        )

        if query.data in (ExchangeCrypto.usdt.name):
            await query.edit_message_text(
                "Выберите сеть",
                reply_markup=build_inline_keyboard(ExchangeNetwork, rows=2),
            )
            return NETWORK

        await query.edit_message_text(
            "Получаете",
            reply_markup=build_inline_keyboard(ExchangeCurrency, rows=2),
        )
    else:
        # curr was chosen
        context.user_data[USER_DATA_KEY][GIVE] = (
            f"Отдаете: {ExchangeCurrency.value_of(query.data)}"
        )
        await query.edit_message_text(
            "Получаете",
            reply_markup=build_inline_keyboard(ExchangeCrypto, rows=3),
        )
    return RECEIVE


async def receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()

    if _is_sell(context):
        # curr was chosen
        context.user_data[USER_DATA_KEY][RECEIVE] = (
            f"Получаете: {ExchangeCurrency.value_of(query.data)}"
        )
    else:
        # crypto was chosen
        context.user_data[USER_DATA_KEY][RECEIVE] = (
            f"Получаете: {ExchangeCrypto.value_of(query.data)}"
        )

        if query.data in (ExchangeCrypto.usdt.name):
            await query.edit_message_text(
                "Выберите сеть",
                reply_markup=build_inline_keyboard(ExchangeNetwork, rows=2),
            )
            return NETWORK

    await query.edit_message_reply_markup(None)
    await approve_user_request(update, context, USER_DATA_KEY)
    return APPROVE


async def network(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    await query.answer()
    net_type = f" (сеть: {ExchangeNetwork.value_of(query.data)})"

    if _is_sell(context):
        context.user_data[USER_DATA_KEY][GIVE] += net_type
        await query.edit_message_text(
            "Получаете",
            reply_markup=build_inline_keyboard(ExchangeCurrency, rows=2),
        )
        return RECEIVE

    context.user_data[USER_DATA_KEY][RECEIVE] += net_type
    await query.edit_message_reply_markup(None)
    await approve_user_request(update, context, USER_DATA_KEY)

    return APPROVE


async def rub_method(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query
    await query.answer()
    method = f" (способ: {PayMethod.value_of(query.data)})"

    if _is_sell(context):
        context.user_data[USER_DATA_KEY][RECEIVE] += method
        await query.edit_message_reply_markup(None)
        await approve_user_request(update, context, USER_DATA_KEY)
        return APPROVE

    context.user_data[USER_DATA_KEY][GIVE] += method
    await query.edit_message_text(
        "Получаете",
        reply_markup=build_inline_keyboard(ExchangeCrypto, rows=3),
    )
    return RECEIVE


async def exchange_approve(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
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
        GIVE: [CallbackQueryHandler(give)],
        RECEIVE: [CallbackQueryHandler(receive)],
        NETWORK: [CallbackQueryHandler(network)],
        RUB_METHOD: [CallbackQueryHandler(rub_method)],
        APPROVE: [CallbackQueryHandler(exchange_approve)],
    },
    fallbacks=default_fallbacks,
    map_to_parent={
        ConversationHandler.END: MAIN_ENTRY_POINT,
    },
    allow_reentry=True,
    name=USER_DATA_KEY,
    persistent=True,
)
