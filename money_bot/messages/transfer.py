from messages.common import StrEnumAsCallback

RUSSIAN_TRANSFER_MESSAGE = (
    "Через нас вы можете отправить любую сумму по России, "
    "в т.ч. Крым, с минимальной комиссией. "
    "Также, мы можем принимать наличные."
)


class ReceiveMethod(StrEnumAsCallback):
    cash = "Наличные 💰"
    bank = "Банковский перевод 🏦"

    @classmethod
    @property
    def cls_name(cls) -> str:  # noqa
        return "Предпочтительный способ получения"
