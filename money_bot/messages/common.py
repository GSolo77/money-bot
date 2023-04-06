from enum import StrEnum


class StrEnumAsCallback(StrEnum):
    @property
    def as_callback(self) -> dict[str, str]:
        """Return dict with data for InlineKeyboardButton (text and
        callback_data).
        """
        return {"text": self.value, "callback_data": self.name}

    @classmethod
    def value_of(cls, attr: str) -> str:
        return getattr(cls, attr).value


class MainButtons(StrEnum):
    exchange = "Операция по обмену 💱"
    russian_transfer = "Отправка по России 🇷🇺"
    abroad_transfer = "Отправка зарубеж 🌍"
    question = "Задать вопрос ❓"


class PayMethod(StrEnumAsCallback):
    cash = "Наличные в Москве 💰"
    bank = "Банковский перевод 🏦"

    @classmethod
    @property
    def cls_name(cls) -> str:  # noqa
        return "Способ оплаты"


class ApprovalButtons(StrEnumAsCallback):
    approve = "✅"
    abort = "❌"


QUESTION_PROMPT_MESSAGE = (
    "Пожалуйста, отправьте ваш вопрос *одним* сообщением. "
)
QUESTION_SUCCESS_MESSAGE = (
    "Спасибо! Ваш вопрос перенаправлен менеджеру, "
    "в ближайшее время с вами свяжутся."
)

START_MESSAGE = (
    "Приветствуем вас в нашем боте. Пожалуйста, выберите услугу:"
)
