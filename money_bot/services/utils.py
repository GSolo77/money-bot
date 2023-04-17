from itertools import permutations
from typing import Iterable

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

SLEEP_TIMEOUT = 0.5


def to_number(update: Update) -> tuple[float | None, bool]:
    """Check if `update.message.text` is convertable to `float`
    and return tuple of `float, False`. Otherwise return
    tuple `conv_step, True`.
    """
    try:
        return float(update.message.text), False
    except ValueError:
        return None, True


def user_request(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    return "\n".join(context.user_data[key].values())


def validate_unique_states(conversations: Iterable[ConversationHandler]):
    for conv1, conv2 in permutations(conversations, r=2):
        if set(conv1.states) & set(conv2.states):
            raise ValueError("Conversations could not share same state")
