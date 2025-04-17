import asyncio
from dotenv import load_dotenv
import os
import logging
import sqlite3
from typing import Final
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares.base import BaseMiddleware

# Load environment and set up directories
load_dotenv()
os.makedirs("media", exist_ok=True)
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME: Final = '@differnet123bot_bot'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class CancelFSMOnNewEventMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state: FSMContext = data.get("state")
        if state and await state.get_state():
            if isinstance(event, Message) and event.text and event.text.startswith('/'):
                await state.clear()
            elif isinstance(event, CallbackQuery):
                await state.clear()
        return await handler(event, data)

dp.message.middleware(CancelFSMOnNewEventMiddleware())
dp.callback_query.middleware(CancelFSMOnNewEventMiddleware())

ADMIN_ROLE = "admin"
USER_ROLE = "user"

COMMANDS_HELP = {
    '/start': 'Starts the bot and gives a welcome message.',
    '/help': 'Shows the list of available commands.',
    '/set_role': 'Set role for a username (admin only).',
    '/delete_user': 'Delete a user by username (admin only).',
    '/reset_password': 'Reset password for a user (admin only).',
    '/whoami': 'Check your current role.',
    '/login': 'Login with username and password.',
    '/open_user': 'Login directly as a user.',
    '/logout': 'Logout and return to user role.',
    '/add_user': 'Add a new user (admin only).',
    '/view_users': 'View all added users (admin only).'
}

class RoleFSM(StatesGroup):
    username = State()
    role = State()

class DeleteUserFSM(StatesGroup):
    username = State()

class ResetPasswordFSM(StatesGroup):
    username = State()
    new_password = State()

class LoginFSM(StatesGroup):
    username = State()
    password = State()

class AddUserFSM(StatesGroup):
    username = State()
    password = State()
    role = State()

CREDENTIALS = {
    "admin123": {"password": "adminpass", "role": ADMIN_ROLE},
    "user123": {"password": "userpass", "role": USER_ROLE},
}

def init_db():
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    for username, data in CREDENTIALS.items():
        c.execute("INSERT OR IGNORE INTO credentials (username, password, role) VALUES (?, ?, ?)", (username, data["password"], data["role"]))
    conn.commit()
    conn.close()

def get_user_role(user_id: int):
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if not result:
        set_user_role(user_id, USER_ROLE)
        return USER_ROLE
    conn.close()
    return result[0]

def set_user_role(user_id: int, role: str):
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    buttons = [
        [InlineKeyboardButton(text="🔐 Login", callback_data="login")],
        [InlineKeyboardButton(text="👤 Continue as User", callback_data="open_user")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Welcome! Please login to continue:", reply_markup=keyboard)

@dp.callback_query(F.data == "login")
async def login_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)

@dp.callback_query(F.data == "open_user")
async def open_user_button(callback: CallbackQuery):
    set_user_role(callback.from_user.id, USER_ROLE)
    await callback.message.answer("✅ You are now logged in as a user. Use /help to see available commands.")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    role = get_user_role(message.from_user.id)
    allowed = [cmd for cmd, desc in COMMANDS_HELP.items() if role == ADMIN_ROLE or cmd not in ["/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"]]
    help_text = "<b>Available Commands:</b>\n\n"
    help_text += '\n'.join(f"{cmd}: {COMMANDS_HELP[cmd]}" for cmd in allowed)
    await message.answer(help_text)

@dp.message(Command("set_role"))
async def cmd_set_role(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to use this command.")
        return
    await message.answer("👤 Enter the target username:")
    await state.set_state(RoleFSM.username)

@dp.message(RoleFSM.username)
async def role_target_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("🎭 Enter role to assign (admin/user):")
    await state.set_state(RoleFSM.role)

@dp.message(RoleFSM.role)
async def role_assign(message: Message, state: FSMContext):
    role = message.text.lower().strip()
    if role not in [ADMIN_ROLE, USER_ROLE]:
        await message.answer("⚠️ Role must be 'admin' or 'user'.")
        return
    data = await state.get_data()
    username = data['username']

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT rowid FROM credentials WHERE username = ?", (username,))
    if not c.fetchone():
        await message.answer("❌ Username not found.")
    else:
        c.execute("UPDATE credentials SET role = ? WHERE username = ?", (role, username))
        await message.answer(f"✅ Role '{role}' assigned to user <b>{username}</b>.")
    conn.commit()
    conn.close()
    await state.clear()

@dp.message(Command("delete_user"))
async def delete_user_command(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to delete users.")
        return
    await message.answer("❌ Enter username to delete:")
    await state.set_state(DeleteUserFSM.username)

@dp.message(DeleteUserFSM.username)
async def delete_user_action(message: Message, state: FSMContext):
    username = message.text.strip()
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("DELETE FROM credentials WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    await message.answer(f"🗑️ User <b>{username}</b> has been deleted.")
    await state.clear()

@dp.message(Command("reset_password"))
async def reset_password_command(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to reset passwords.")
        return
    await message.answer("🔐 Enter username to reset password:")
    await state.set_state(ResetPasswordFSM.username)

@dp.message(ResetPasswordFSM.username)
async def reset_password_get_new(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("🆕 Enter new password:")
    await state.set_state(ResetPasswordFSM.new_password)

@dp.message(ResetPasswordFSM.new_password)
async def reset_password_apply(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data['username']
    new_password = message.text.strip()

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("UPDATE credentials SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

    await message.answer(f"🔑 Password for <b>{username}</b> has been reset.")
    await state.clear()

@dp.message(Command("whoami"))
async def cmd_whoami(message: Message):
    role = get_user_role(message.from_user.id)
    await message.answer(f"🧾 Your role is: <b>{role}</b>")

@dp.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    await message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)

@dp.message(LoginFSM.username)
async def login_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("🔒 Enter your password:")
    await state.set_state(LoginFSM.password)

@dp.message(LoginFSM.password)
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
        await message.answer(f"✅ Login successful! Role: {role}\nTo see available commands, use /help.")
    else:
        await message.answer("❌ Invalid credentials.")
    await state.clear()

@dp.message(Command("open_user"))
async def open_as_user(message: Message):
    set_user_role(message.from_user.id, USER_ROLE)
    await message.answer("✅ You are now logged in as a user.")

@dp.message(Command("logout"))
async def logout_command(message: Message):
    set_user_role(message.from_user.id, USER_ROLE)
    await message.answer("🚪 You have been logged out. Role set to user.")

@dp.message(Command("add_user"))
async def cmd_add_user(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to add users.")
        return
    await message.answer("🧑 Enter a new username:")
    await state.set_state(AddUserFSM.username)

@dp.message(AddUserFSM.username)
async def add_user_username(message: Message, state: FSMContext):
    username = message.text.strip()
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT username FROM credentials WHERE username = ?", (username,))
    if c.fetchone():
        await message.answer("⚠️ Username already exists. Please use a different one.")
        conn.close()
        return
    conn.close()
    await state.update_data(username=username)
    await message.answer("🔑 Enter a password for the user:")
    await state.set_state(AddUserFSM.password)

@dp.message(AddUserFSM.password)
async def add_user_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text.strip())
    await message.answer("🎭 Enter role (admin/user):")
    await state.set_state(AddUserFSM.role)

@dp.message(AddUserFSM.role)
async def add_user_role(message: Message, state: FSMContext):
    role = message.text.lower().strip()
    if role not in [ADMIN_ROLE, USER_ROLE]:
        await message.answer("⚠️ Role must be 'admin' or 'user'.")
        return
    data = await state.get_data()
    username = data['username']
    password = data['password']

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("INSERT INTO credentials (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

    await message.answer(f"✅ User <b>{username}</b> added with role <b>{role}</b>.")
    await state.clear()

@dp.message(Command("view_users"))
async def view_users(message: Message):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to view users.")
        return
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT username, role FROM credentials")
    users = c.fetchall()
    conn.close()

    if not users:
        await message.answer("No users found.")
    else:
        text = "\n".join(f"👤 <b>{u}</b>: {r}" for u, r in users)
        await message.answer(f"<b>Users:</b>\n\n{text}")

async def main():
    init_db()
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")
