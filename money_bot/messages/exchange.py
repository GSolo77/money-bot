from messages.common import StrEnumAsCallback


class ExchangeType(StrEnumAsCallback):
    buy_usdt = "Купить USDT 📥"
    sell_usdt = "Продать USDT 📤"

    @classmethod
    @property
    def cls_name(cls) -> str:  # noqa
        return "Тип сделки"


class ExchangeCurrency(StrEnumAsCallback):
    rub = "RUB 🇷🇺"
    usd = "USD 🇺🇸"
    eur = "EUR 🇪🇺"
    cny = "CNY 🇨🇳"

    @classmethod
    @property
    def cls_name(cls) -> str:  # noqa
        return "Валюта"


class ExchangeNetwork(StrEnumAsCallback):
    trc20 = "TRC20"
    erc20 = "ERC20"
    bep20 = "BEP20"
    skip = "Пропустить"

    @classmethod
    @property
    def cls_name(cls) -> str:  # noqa
        return "Сеть"


EXCHANGE_INFO_MESSAGE = (
    "Мы обмениваем рубли/доллары/евро/юани на USDT и обратно. "
    "Возможно проведение сделки с наличными в Москве."
)
