from messages.common import StrEnumAsCallback

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
