from enum import StrEnum

from telegram import Message
from telegram.ext.filters import MessageFilter


class ButtonsFilter(MessageFilter):
    __slots__ = ("buttons_texts",)

    def __init__(self, *buttons: StrEnum) -> None:
        self.buttons_texts = [str(button) for button in buttons]
        super().__init__()

    def filter(self, message: Message) -> bool | dict[str, list] | None:
        if not message.text:
            return False
        return any(
            message.text.startswith(button) for button in self.buttons_texts
        )
