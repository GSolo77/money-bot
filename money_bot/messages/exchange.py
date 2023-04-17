from messages.common import StrEnumAsCallback


class ExchangeType(StrEnumAsCallback):
    buy_usdt = "Купить USDT 📥"
    sell_usdt = "Продать USDT 📤"


class ExchangeCurrency(StrEnumAsCallback):
    rub = "RUB 🇷🇺"
    usd = "USD 🇺🇸"
    eur = "EUR 🇪🇺"
    cny = "CNY 🇨🇳"
    byn = "BYN 🇧🇾"
    thb = "THB 🇹🇭"


class ExchangeNetwork(StrEnumAsCallback):
    trc20 = "TRC20"
    erc20 = "ERC20"
    bep20 = "BEP20"
    skip = "Пропустить"


EXCHANGE_INFO_MESSAGE = (
    "Мы обмениваем рубли/доллары/евро/юани на USDT и обратно. "
    "Возможно проведение сделки с наличными в Москве."
)
