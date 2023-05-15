from messages.common import StrEnumAsCallback


class ExchangeType(StrEnumAsCallback):
    buy = "Покупка 📥"
    sell = "Продажа 📤"


class ExchangeCrypto(StrEnumAsCallback):
    btc = "BTC"
    usdt = "USDT"
    usdc = "USDC"
    eth = "ETH"
    xmr = "XMR"
    BNB = "BNB"


class ExchangeCurrency(StrEnumAsCallback):
    rub = "RUB 🇷🇺"
    usd = "USD 🇺🇸"


class ExchangeNetwork(StrEnumAsCallback):
    trc20 = "TRC20"
    erc20 = "ERC20"
    bep20 = "BEP20"
    skip = "Пропустить"


EXCHANGE_INFO_MESSAGE = (
    "Мы покупаем и продаем различные криптовалюты:\n"
    " - за рубли: наличные в Москве/безналичные практически в любой банк\n"
    " - за доллары: только наличные в Москве"
)
