from enum import StrEnum

from telegram import Message
from telegram.ext import filters

from messages.common import MainButtons


class ButtonsFilter(filters.MessageFilter):
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


TEXT_NOT_CMND_NOR_BTN = (
    filters.TEXT & ~filters.COMMAND & ~ButtonsFilter(*MainButtons)
)
ALL_NOT_CMND_NOR_BTN = (
    filters.ALL & ~filters.COMMAND & ~ButtonsFilter(*MainButtons)
)
