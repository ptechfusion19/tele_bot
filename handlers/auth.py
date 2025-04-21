# handlers/auth.py

import sqlite3

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import LoginFSM
from database import get_user_role, set_user_role
from keyboards import build_start_keyboard, build_command_keyboard


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Send the welcome message with login options."""
    await message.answer("Welcome! Please login to continue:", reply_markup=build_start_keyboard())


@router.callback_query(F.data == "/start")
async def cmd_start_button(callback: CallbackQuery):
    await callback.message.answer("Welcome! Please login to continue:", reply_markup=build_start_keyboard())
    await callback.answer()


@router.callback_query(F.data == "login")
async def login_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)
    await callback.answer()


@router.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    await message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)


@router.message(LoginFSM.username)
async def login_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("🔒 Enter your password:")
    await state.set_state(LoginFSM.password)


@router.message(LoginFSM.password)
async def login_password(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username")
    password = message.text.strip()

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT password, role FROM credentials WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == password:
        role = result[1]
        set_user_role(message.from_user.id, role)
        keyboard = build_command_keyboard(role)
        await message.answer(
            f"✅ Login successful as <b>{username}</b> (<i>{role}</i>)\n\n👇 Available commands:",
            reply_markup=keyboard
        )
    else:
        await message.answer("❌ Invalid credentials.")

    await state.clear()


@router.callback_query(F.data == "/login")
async def callback_login(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)
    await callback.answer()


@router.message(Command("logout"))
async def logout_command(message: Message):
    set_user_role(message.from_user.id, "user")
    await message.answer("🚪 You have been logged out. Role set to user.")


@router.callback_query(F.data == "/logout")
async def logout_callback(callback: CallbackQuery):
    set_user_role(callback.from_user.id, "user")
    await callback.message.answer("🚪 You have been logged out. Role set to user.")
    await callback.answer()


@router.message(Command("open_user"))
async def open_as_user(message: Message):
    set_user_role(message.from_user.id, "user")
    await message.answer("✅ You are now logged in as a user.")


@router.callback_query(F.data == "/open_user")
async def open_as_user_callback(callback: CallbackQuery):
    set_user_role(callback.from_user.id, "user")
    await callback.message.answer("✅ You are now logged in as a user. Use /help to see available commands.")
    await callback.answer()


@router.message(Command("whoami"))
async def cmd_whoami(message: Message):
    role = get_user_role(message.from_user.id)
    await message.answer(f"🧾 Your role is: <b>{role}</b>")


@router.callback_query(F.data == "/whoami")
async def cmd_whoami_callback(callback: CallbackQuery):
    role = get_user_role(callback.from_user.id)
    await callback.message.answer(f"🧾 Your role is: <b>{role}</b>")
    await callback.answer()
