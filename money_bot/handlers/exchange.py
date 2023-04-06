import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from config import TELEGRAM_MANAGER_ID
from filters import ButtonsFilter
from handlers.cancel import cancel
from handlers.keyboards import EXCHANGE_INIT_KEYBOARD, \
    EXCHANGE_CURRENCY_KEYBOARD, PAY_METHOD_KEYBOARD, APPROVE_KEYBOARD, \
    EXCHANGE_NETWORK_KEYBOARD, MAIN_KEYBOARD
from messages.common import ApprovalButtons, MainButtons, PayMethod
from messages.exchange import ExchangeType, ExchangeCurrency, \
    ExchangeNetwork, EXCHANGE_INFO_MESSAGE
from services.exceptions import RequiredDataMissing

logger = logging.getLogger(__name__)

USER_DATA_KEY = 'exchange_request'
TYPE, CURRENCY, METHOD, AMOUNT, NETWORK, APPROVE, RESULT = 1, 2, 3, 4, 5, 6, 7
STEPS_CALLBACK_MAPPING = {
    TYPE: ExchangeType,
    CURRENCY: ExchangeCurrency,
    NETWORK: ExchangeNetwork,
    METHOD: PayMethod,
}


def _build_exchange_request_message(user_data: dict[int, str]) -> str:
    if user_data.keys() != STEPS_CALLBACK_MAPPING.keys():
        raise RequiredDataMissing

    message = [
        f"{btn_enum.cls_name}:  {btn_enum.value_of(user_data[step])}"
        for step, btn_enum in STEPS_CALLBACK_MAPPING.items()
    ]

    return "\n".join(message)


async def exchange(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info('exchange. user_data %s', context.user_data)
    await update.message.reply_text(
        EXCHANGE_INFO_MESSAGE,
        reply_markup=EXCHANGE_INIT_KEYBOARD,
    )

    return CURRENCY


async def choose_currency(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY] = {}
    context.user_data[USER_DATA_KEY][TYPE] = query.data
    await query.answer()
    logger.info("currency. user_data %s", context.user_data)
    await query.edit_message_text(
        "Выберите валюту оплаты",
        reply_markup=EXCHANGE_CURRENCY_KEYBOARD,
    )

    return METHOD


async def choose_method(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][CURRENCY] = query.data
    await query.answer()
    logger.info("type. user_data %s", context.user_data)
    await query.edit_message_text(
        "Выберите тип оплаты",
        reply_markup=PAY_METHOD_KEYBOARD,
    )

    return NETWORK


async def choose_network(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][METHOD] = query.data
    await query.answer()
    logger.info('network. user_data %s', context.user_data)
    await query.edit_message_text(
        "Выберите сеть",
        reply_markup=EXCHANGE_NETWORK_KEYBOARD,
    )

    return APPROVE


async def approve_exchange_request(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    context.user_data[USER_DATA_KEY][NETWORK] = query.data
    await query.answer()
    logger.info('approve. user_data %s', context.user_data)
    user_final_request = _build_exchange_request_message(
        context.user_data[USER_DATA_KEY],
    )
    await query.edit_message_text(
        f"Ваша заявка:\n\n{user_final_request}\n\nПодтвердить?",
        reply_markup=APPROVE_KEYBOARD,
    )

    return RESULT


async def result_exchange_result(update: Update,
                                 context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.message.edit_reply_markup(None)

    if query.data == ApprovalButtons.approve.name:
        message_text = "Ваша заявка успешно отправлена!"
        user = update.effective_user
        user_final_request = (
            f"Заявка пользователя {user.last_name} {user.first_name} "
            f"(@{user.username}):\n\n"
        )
        user_final_request += _build_exchange_request_message(
            context.user_data[USER_DATA_KEY],
        )
        await context.bot.send_message(
            TELEGRAM_MANAGER_ID,
            user_final_request,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        message_text = "Отменено"

    await query.message.reply_text(message_text, reply_markup=MAIN_KEYBOARD)

    return ConversationHandler.END


exchange_conv = ConversationHandler(
    entry_points=[
        CommandHandler("exchange", exchange),
        MessageHandler(filters.Regex(MainButtons.exchange), exchange),
    ],
    states={
        CURRENCY: [CallbackQueryHandler(choose_currency)],
        METHOD: [CallbackQueryHandler(choose_method)],
        NETWORK: [CallbackQueryHandler(choose_network)],
        APPROVE: [CallbackQueryHandler(approve_exchange_request)],
        RESULT: [CallbackQueryHandler(result_exchange_result)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(ButtonsFilter(*MainButtons), cancel)
    ],
    allow_reentry=True,
    name='exchange_dialog',
    persistent=True,
)
