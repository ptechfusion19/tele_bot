# middlewares.py
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


class CancelFSMOnNewEventMiddleware(BaseMiddleware):
    """
    Middleware to automatically cancel any active FSM state when a new event
    such as a command message or callback query is received.
    """
    async def __call__(self, handler, event, data):
        state: FSMContext = data.get("state")

        if state and await state.get_state():
            if isinstance(event, Message) and event.text and event.text.startswith('/'):
                await state.clear()
            elif isinstance(event, CallbackQuery):
                await state.clear()

        return await handler(event, data)