from typing import Type, Sequence

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton

from messages.common import MainButtons, StrEnumAsCallback

MAIN_KEYBOARD = ReplyKeyboardMarkup.from_column(
    button_column=(
        MainButtons.exchange,
        MainButtons.abroad_transfer,
        MainButtons.question,
    ),
    one_time_keyboard=True,
    resize_keyboard=True,
)
CANCEL_KEYBOARD = ReplyKeyboardMarkup.from_column(
    button_column=(MainButtons.back_to_menu,),
    resize_keyboard=True,
    one_time_keyboard=True,
    is_persistent=True,
)


def _chunks(seq: Sequence, chunks_num: int) -> list[list]:
    d, r = divmod(len(seq), chunks_num)
    res = []
    for i in range(chunks_num):
        si = (d + 1) * (i if i < r else r) + d * (0 if i < r else i - r)
        res.append(seq[si:si + (d + 1 if i < r else d)])
    return res


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
        # keep include names order
        enums = [getattr(buttons_enum, name) for name in include_names]
        print('enums', enums)
    elif exclude_names:
        enums = filter(
            lambda item: item.name not in exclude_names, buttons_enum
        )
    else:
        enums = buttons_enum

    inline_buttons = [
        InlineKeyboardButton(**enum_item.as_callback) for enum_item in enums
    ]

    return InlineKeyboardMarkup(inline_keyboard=_chunks(inline_buttons, rows))
