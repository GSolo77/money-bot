import logging
import sys
from functools import wraps
from typing import Iterable

from telegram.ext import ConversationHandler

logger = logging.getLogger(__name__)


def conversation_entry_point(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug("Entered conversation in %s", func.__name__)
        return await func(*args, **kwargs)
    return wrapper


def conversation_state(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug("Entered conversation state in %s", func.__name__)
        return await func(*args, **kwargs)
    return wrapper


def debug_conversation_handlers(handlers: Iterable[ConversationHandler]):
    if '--debug' not in sys.argv:
        return

    for conversation_handler in handlers:
        for entry in conversation_handler.entry_points:
            entry.callback = conversation_entry_point(entry.callback)

        for states in conversation_handler.states.values():
            for state_handler in states:
                state_handler.callback = conversation_state(
                    state_handler.callback
                )
