import asyncio
from dotenv import load_dotenv
import os
import logging
import sqlite3
from typing import Final
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram import types

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
    '/view_users': 'View all added users (admin only).',
    '/submit_review': 'Submit a review.',
    '/view_reviews': 'View all reviews (admin only).',
    '/media': 'Send media files.',
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
    
class SubmitReviewFSM(StatesGroup):
    name = State()
    email = State()
    rating = State()
    comment = State()

CREDENTIALS = {
    "admin123": {"password": "adminpass", "role": ADMIN_ROLE},
    "user123": {"password": "userpass", "role": USER_ROLE},
}

def init_db():
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    email TEXT,
                    rating INTEGER,
                    comment TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                 )''')
    
    for username, data in CREDENTIALS.items():
        c.execute("INSERT OR IGNORE INTO credentials (username, password, role) VALUES (?, ?, ?)", 
                  (username, data["password"], data["role"]))
        
        # Correct the insert for the users table. Fetch user_id based on the username from credentials
        c.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES ((SELECT rowid FROM credentials WHERE username = ?), ?)", 
                  (username, data["role"]))
    
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

@router.callback_query(F.data == "/start")
async def cmd_start_button(callback: CallbackQuery):
    buttons = [
        [InlineKeyboardButton(text="🔐 Login", callback_data="login")],
        [InlineKeyboardButton(text="👤 Continue as User", callback_data="open_user")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("Welcome! Please login to continue:", reply_markup=keyboard)
    await callback.answer()
 
@dp.callback_query(F.data == "login")
async def login_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)
    
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

        keyboard = build_command_keyboard(role)

        await message.answer(
            f"✅ Login successful as <b>{username}</b> (<i>{role}</i>)\n\n👇 Available commands:",
            reply_markup=keyboard
        )
    else:
        await message.answer("❌ Invalid credentials.")

    await state.clear()


def build_command_keyboard(role: str):
    user_buttons = []
    admin_buttons = []

    for cmd, desc in COMMANDS_HELP.items():
        btn = InlineKeyboardButton(text=cmd, callback_data=cmd)
        if role == ADMIN_ROLE or cmd not in ["/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"]:
            if cmd in ["/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"]:
                admin_buttons.append(btn)
            else:
                user_buttons.append(btn)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        user_buttons[i:i+2] for i in range(0, len(user_buttons), 2)
    ] + ([
        [InlineKeyboardButton(text="🔐 Admin Panel", callback_data="ignore_admin_title")]
    ] if admin_buttons else []) + [
        admin_buttons[i:i+2] for i in range(0, len(admin_buttons), 2)
    ])
    return markup

@dp.callback_query(F.data == "/help")
async def cmd_help_callback(callback: CallbackQuery):
    role = get_user_role(callback.from_user.id)
    allowed = [cmd for cmd, desc in COMMANDS_HELP.items() if role == ADMIN_ROLE or cmd not in ["/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"]]
    help_text = "<b>Available Commands:</b>\n\n"
    help_text += '\n'.join(f"{cmd}: {COMMANDS_HELP[cmd]}" for cmd in allowed)
    await callback.message.answer(help_text)
    
@dp.callback_query(F.data == "/whoami")
async def cmd_whoami_callback(callback: CallbackQuery):
    role = get_user_role(callback.from_user.id)
    await callback.message.answer(f"🧾 Your role is: <b>{role}</b>")
    
@dp.callback_query(F.data == "/open_user")
async def open_as_user_callback(callback: CallbackQuery):
    set_user_role(callback.from_user.id, USER_ROLE)
    await callback.message.answer("✅ You are now logged in as a user.Use /help to see available commands.")
    await callback.answer()  
    
@dp.callback_query(F.data == "/logout")
async def logout_callback(callback: CallbackQuery):
    set_user_role(callback.from_user.id, USER_ROLE)
    await callback.message.answer("🚪 You have been logged out. Role set to user.")
    await callback.answer() 
    
@dp.callback_query(F.data == "/submit_review")
async def submit_review_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please provide your name:")
    await state.set_state(SubmitReviewFSM.name)
    await callback.answer()
    
@dp.callback_query(F.data == "/view_reviews")
async def view_reviews_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    role = get_user_role(user_id)

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()

    if role == ADMIN_ROLE:
        c.execute('''SELECT credentials.username, reviews.name, reviews.email, reviews.rating, reviews.comment 
                     FROM reviews
                     JOIN credentials ON reviews.user_id = credentials.rowid''')
    else:
        c.execute('''SELECT reviews.name, reviews.email, reviews.rating, reviews.comment 
                     FROM reviews 
                     WHERE reviews.user_id = ?''', (user_id,))

    reviews = c.fetchall()
    conn.close()

    if reviews:
        review_text = ""
        for rev in reviews:
            if role == ADMIN_ROLE:
                review_text += f"👤 User: {rev[0]}\n📛 Name: {rev[1]}\n📧 Email: {rev[2]}\n⭐ Rating: {rev[3]}/5\n💬 Comment: {rev[4]}\n\n"
            else:
                review_text += f"📛 Name: {rev[0]}\n📧 Email: {rev[1]}\n⭐ Rating: {rev[2]}/5\n💬 Comment: {rev[3]}\n\n"

        await callback.message.answer(f"<b>Reviews:</b>\n\n{review_text}", parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer("No reviews found.")
    
    await callback.answer()
    
@dp.callback_query(F.data == "/set_role")
async def callback_set_role(callback: CallbackQuery, state: FSMContext):
    if get_user_role(callback.from_user.id) != ADMIN_ROLE:
        await callback.message.answer("🚫 You do not have permission to use this.")
        await callback.answer()
        return

    await callback.message.answer("👤 Enter the target username:")
    await state.set_state(RoleFSM.username)
    await callback.answer()   
    
@dp.callback_query(F.data == "/delete_user")
async def callback_delete_user(callback: CallbackQuery, state: FSMContext):
    if get_user_role(callback.from_user.id) != ADMIN_ROLE:
        await callback.message.answer("🚫 You do not have permission to delete users.")
        await callback.answer()
        return

    await callback.message.answer("❌ Enter username to delete:")
    await state.set_state(DeleteUserFSM.username)
    await callback.answer()
    
@dp.callback_query(F.data == "/reset_password")
async def callback_reset_password(callback: CallbackQuery, state: FSMContext):
    if get_user_role(callback.from_user.id) != ADMIN_ROLE:
        await callback.message.answer("🚫 You do not have permission to reset passwords.")
        await callback.answer()
        return

    await callback.message.answer("🔐 Enter username to reset password:")
    await state.set_state(ResetPasswordFSM.username)
    await callback.answer()  # Acknowledge callback

@dp.callback_query(F.data == "/add_user")
async def callback_add_user(callback: CallbackQuery, state: FSMContext):
    if get_user_role(callback.from_user.id) != ADMIN_ROLE:
        await callback.message.answer("🚫 You do not have permission to add users.")
        await callback.answer()
        return

    await callback.message.answer("🧑 Enter a new username:")
    await state.set_state(AddUserFSM.username)
    await callback.answer()
    
@dp.callback_query(F.data == "/view_users")
async def callback_view_users(callback: CallbackQuery):
    if get_user_role(callback.from_user.id) != ADMIN_ROLE:
        await callback.message.answer("🚫 You do not have permission to view users.")
        await callback.answer()
        return
    
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT username, role FROM credentials")
    users = c.fetchall()
    conn.close()

    if not users:
        await callback.message.answer("No users found.")
    else:
        text = "\n".join(f"👤 <b>{u}</b>: {r}" for u, r in users)
        await callback.message.answer(f"<b>Users:</b>\n\n{text}")

    await callback.answer()  # Acknowledge the callback

@dp.callback_query(F.data == "/login")
async def callback_login(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🧑 Enter your username:")
    await state.set_state(LoginFSM.username)
    await callback.answer()  # Acknowledge the callback
            
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


@dp.message(Command("submit_review"))
async def submit_review_command(message: Message, state: FSMContext):
    await message.answer("Please provide your name:")
    await state.set_state(SubmitReviewFSM.name)

@dp.message(SubmitReviewFSM.name)
async def ask_for_email(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Please provide your email:")
    await state.set_state(SubmitReviewFSM.email)

@dp.message(SubmitReviewFSM.email)
async def ask_for_rating(message: Message, state: FSMContext):
    await state.update_data(email=message.text.strip())
    await message.answer("Please provide a rating from 1 to 5:")
    await state.set_state(SubmitReviewFSM.rating)

@dp.message(SubmitReviewFSM.rating)
async def ask_for_comment(message: Message, state: FSMContext):
    rating = message.text.strip()
    if not rating.isdigit() or not 1 <= int(rating) <= 5:
        await message.answer("Rating must be a number between 1 and 5. Please provide a valid rating:")
        return
    
    await state.update_data(rating=int(rating))
    await message.answer("Please provide your comment:")
    await state.set_state(SubmitReviewFSM.comment)

@dp.message(SubmitReviewFSM.comment)
async def save_review(message: Message, state: FSMContext):
    data = await state.get_data()
    
    name = data['name']
    email = data['email']
    rating = data['rating']
    comment = message.text.strip()
    user_id = message.from_user.id
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute('''INSERT INTO reviews (user_id, name, email, rating, comment)
                 VALUES (?, ?, ?, ?, ?)''', (user_id, name, email, rating, comment))
    conn.commit()
    conn.close()

    await message.answer("✅ Your review has been submitted successfully!")
    await state.clear()

async def view_reviews(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    role = get_user_role(user_id)
    
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()

    if role == ADMIN_ROLE:
        c.execute('''SELECT credentials.username, reviews.name, reviews.email, reviews.rating, reviews.comment 
                     FROM reviews
                     JOIN credentials ON reviews.user_id = credentials.rowid''')
    else:
        c.execute('''SELECT reviews.name, reviews.email, reviews.rating, reviews.comment 
                     FROM reviews 
                     WHERE reviews.user_id = ?''', (user_id,))
    
    reviews = c.fetchall()
    conn.close()

    if reviews:
        review_text = ""
        for rev in reviews:
            if role == ADMIN_ROLE:
                
                review_text += f"User: {rev[0]} | Name: {rev[1]} | Email: {rev[2]} | Rating: {rev[3]} | Comment: {rev[4]}\n\n"
            else:
                
                review_text += f"Name: {rev[0]} | Email: {rev[1]} | Rating: {rev[2]} | Comment: {rev[3]}\n\n"

        
        await message.answer(f"Reviews:\n{review_text}", parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("No reviews found.")


@dp.message(Command("view_reviews"))
async def view_reviews(message: Message):
    conn = sqlite3.connect("roles.db") 
    cursor = conn.cursor()

    cursor.execute("SELECT name, rating, comment FROM reviews")
    reviews = cursor.fetchall()
    conn.close()

    if not reviews:
        await message.answer("No reviews yet.")
    else:
        response = "\n\n".join(
            [f"Name: {r[0]}\nRating: {r[1]}/5\nComment: {r[2]}" for r in reviews]
        )
        await message.answer(response)


@router.message(Command("media"))
async def show_media_options(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📸 Photo", callback_data="send_photo"),
            InlineKeyboardButton(text="🎬 Video", callback_data="send_video")
        ],
        [
            InlineKeyboardButton(text="🎵 Audio", callback_data="send_audio"),
            InlineKeyboardButton(text="📄 Document", callback_data="send_doc")
        ]
    ])
    await message.answer("Select a media type to send:", reply_markup=keyboard)

@router.callback_query(F.data == "/media")
async def media_button_clicked(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📸 Photo", callback_data="send_photo"),
            InlineKeyboardButton(text="🎬 Video", callback_data="send_video")
        ],
        [
            InlineKeyboardButton(text="🎵 Audio", callback_data="send_audio"),
            InlineKeyboardButton(text="📄 Document", callback_data="send_doc")
        ]
    ])
    await callback.message.answer("Select a media type to send:", reply_markup=keyboard)
    await callback.answer()
    
    
@router.callback_query(F.data == "send_photo")
async def handle_send_photo(callback: CallbackQuery):
    file = FSInputFile("media/download.png")
    await callback.message.answer_photo(file, caption="📸 Sample photo!")
    await callback.answer()

@router.callback_query(F.data == "send_video")
async def handle_send_video(callback: CallbackQuery):
    file = FSInputFile("media/sample_video.mp4")
    await callback.message.answer_video(file, caption="🎬 Sample video!")
    await callback.answer()

@router.callback_query(F.data == "send_audio")
async def handle_send_audio(callback: CallbackQuery):
    file = FSInputFile("media/sample_audio.mp3")
    await callback.message.answer_audio(file, caption="🎵 Sample audio!")
    await callback.answer()

@router.callback_query(F.data == "send_doc")
async def handle_send_doc(callback: CallbackQuery):
    file = FSInputFile("media/sample_doc.doc")
    await callback.message.answer_document(file, caption="📄 Sample document!")
    await callback.answer()
dp.include_router(router)
async def main():
    init_db()
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")  