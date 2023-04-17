from messages.common import StrEnumAsCallback

RUSSIAN_TRANSFER_MESSAGE = (
    "Через нас вы можете отправить любую сумму по России, "
    "в т.ч. Крым, с минимальной комиссией. "
    "Также, мы можем принимать наличные."
)

ABROAD_TRANSFER_MESSAGE = (
    "Отправка рублей и валюты в любую точку мира, любая сумма. "
    "Возможен прием наличных."
)


class ReceiveMethod(StrEnumAsCallback):
    cash = "Наличные 💰"
    bank = "Банковский перевод 🏦"


class OriginCurrency(StrEnumAsCallback):
    rub = "RUB 🇷🇺"
    usd = "USD 🇺🇸"
    eur = "EUR 🇪🇺"
    cny = "CNY 🇨🇳"
    aed = "AED 🇦🇪"
    byn = "BYN 🇧🇾"
    thd = "THD 🇹🇭"
    local = "Местная"
    other = "Другая"


class RecipientType(StrEnumAsCallback):
    individual = "Физ. лицо 👤"
    business = "Юр. лицо 👨‍💼"
