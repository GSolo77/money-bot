from messages.common import StrEnumAsCallback


class ExchangeType(StrEnumAsCallback):
    buy = "Покупка 📥"
    sell = "Продажа 📤"


class ExchangeCrypto(StrEnumAsCallback):
    usdt = "USDT"


class ExchangeCurrency(StrEnumAsCallback):
    rub = "RUB 🇷🇺"
    usd = "USD 🇺🇸"


class ExchangeNetwork(StrEnumAsCallback):
    trc20 = "TRC20"
    erc20 = "ERC20"
    bep20 = "BEP20"
    skip = "Пропустить"


EXCHANGE_INFO_MESSAGE = (
    "Мы покупаем и продаем USDT и другие криптовалюты:\n"
    " - за наличные рубли\n"
    " - за наличные доллары"
)
