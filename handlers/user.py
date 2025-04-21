# handlers/user.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database import get_user_role
from config import COMMANDS_HELP, ADMIN_ROLE

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Send a list of available commands based on user role."""
    role = get_user_role(message.from_user.id)
    allowed = [
        cmd for cmd in COMMANDS_HELP
        if role == ADMIN_ROLE or cmd not in [
            "/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"
        ]
    ]
    help_text = "<b>Available Commands:</b>\n\n"
    help_text += '\n'.join(f"{cmd}: {COMMANDS_HELP[cmd]}" for cmd in allowed)
    await message.answer(help_text)


@router.callback_query(F.data == "/help")
async def cmd_help_callback(callback: CallbackQuery):
    """Send help text in response to inline button (callback)."""
    role = get_user_role(callback.from_user.id)
    allowed = [
        cmd for cmd in COMMANDS_HELP
        if role == ADMIN_ROLE or cmd not in [
            "/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"
        ]
    ]
    help_text = "<b>Available Commands:</b>\n\n"
    help_text += '\n'.join(f"{cmd}: {COMMANDS_HELP[cmd]}" for cmd in allowed)
    await callback.message.answer(help_text)
    await callback.answer()
