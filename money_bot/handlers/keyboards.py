from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton

from messages.common import MainButtons, ApprovalButtons, PayMethod
from messages.exchange import ExchangeType, ExchangeCurrency, ExchangeNetwork
from messages.transfer import ReceiveMethod

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=(
        (MainButtons.exchange, MainButtons.russian_transfer),
        (MainButtons.abroad_transfer, MainButtons.question),
    ),
    one_time_keyboard=True,
)

EXCHANGE_INIT_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=(
        (InlineKeyboardButton(**ExchangeType.buy_usdt.as_callback),),
        (InlineKeyboardButton(**ExchangeType.sell_usdt.as_callback),)
    ),
)

EXCHANGE_CURRENCY_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=(
        (
            InlineKeyboardButton(**ExchangeCurrency.rub.as_callback),
            InlineKeyboardButton(**ExchangeCurrency.usd.as_callback),
        ),
        (
            InlineKeyboardButton(**ExchangeCurrency.eur.as_callback),
            InlineKeyboardButton(**ExchangeCurrency.cny.as_callback),
        ),
    ),
)

PAY_METHOD_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=(
        (InlineKeyboardButton(**PayMethod.cash.as_callback),),
        (InlineKeyboardButton(**PayMethod.bank.as_callback),)
    ),
)

RECEIVE_METHOD_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=(
        (InlineKeyboardButton(**ReceiveMethod.cash.as_callback),),
        (InlineKeyboardButton(**ReceiveMethod.bank.as_callback),),
    ),
)

EXCHANGE_NETWORK_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=(
        (
            InlineKeyboardButton(**ExchangeNetwork.trc20.as_callback),
            InlineKeyboardButton(**ExchangeNetwork.bep20.as_callback),
        ),
        (
            InlineKeyboardButton(**ExchangeNetwork.erc20.as_callback),
            InlineKeyboardButton(**ExchangeNetwork.skip.as_callback),
        ),
    ),
)

APPROVE_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=(
        (
            InlineKeyboardButton(**ApprovalButtons.approve.as_callback),
            InlineKeyboardButton(**ApprovalButtons.abort.as_callback),
        ),
    ),
)
