from typing import Type

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton, KeyboardButton

from messages.common import MainButtons, StrEnumAsCallback

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=(
        (MainButtons.exchange, MainButtons.russian_transfer),
        (MainButtons.abroad_transfer, MainButtons.question),
    ),
    one_time_keyboard=True,
    resize_keyboard=True,
)
CANCEL_KEYBOARD = ReplyKeyboardMarkup.from_button(
    KeyboardButton(MainButtons.back_to_menu),
    resize_keyboard=True,
    one_time_keyboard=True,
    is_persistent=True,
)


def build_inline_keyboard(
        buttons_enum: Type[StrEnumAsCallback],
        *,
        rows: int,
        include_names: list['str'] = None,
        exclude_names: list['str'] = None,
) -> InlineKeyboardMarkup:
    if include_names and exclude_names:
        raise ValueError('Can not pass both include_names and exclude_names')

    if include_names:
        enums = filter(lambda item: item.name in include_names, buttons_enum)
    elif exclude_names:
        enums = filter(
            lambda item: item.name not in exclude_names, buttons_enum
        )
    else:
        enums = buttons_enum

    inline_buttons = [
        InlineKeyboardButton(**enum_item.as_callback) for enum_item in enums
    ]
    chunked_inline_buttons = [inline_buttons[i::rows] for i in range(rows)]

    return InlineKeyboardMarkup(inline_keyboard=chunked_inline_buttons)
