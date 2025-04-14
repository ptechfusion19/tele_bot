import asyncio
import logging
import sqlite3
from typing import Final
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN: Final = '8016112194:AAEYKqbIHjIHnqd-T77JktYG2C8vJVCsqHE'.strip()
BOT_USERNAME: Final = '@differnet123bot_bot'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

COMMANDS_HELP = {
    '/start': 'Starts the bot and gives a welcome message.',
    '/help': 'Shows the list of available commands.',
    '/custom': 'A custom reply.',
    '/info': 'Information about the bot.',
    '/echo': 'Echoes your message.',
    '/buttons': 'Inline buttons demo.',
    '/begin': 'Start a conversation to collect name/email.',
    '/cancel': 'Cancel the conversation.',
    '/review': 'Leave a review.',
    '/view_reviews': 'View all reviews.',
}

class Form(StatesGroup):
    name = State()
    email = State()
    confirm = State()

class ReviewForm(StatesGroup):
    name = State()
    email = State()
    rating = State()
    comment = State()

import sqlite3
import os

def init_db():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            rating INTEGER,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Submit Review", callback_data="submit_review")], [InlineKeyboardButton(text="📋 Review ", callback_data="review")]
       
    ])
    await message.answer(
        "<b>Welcome!</b> 👋\n\nI'm your assistant bot.if you need help press /help ....\nFor the purpose of adding review..Choose an option below:",
        reply_markup=keyboard
    )

@dp.message(Command('help'))
async def cmd_help(message: Message):
    text = "<b>Here are the commands I support:</b>\n\n"
    text += '\n'.join(f"{cmd}: {desc}" for cmd, desc in COMMANDS_HELP.items())
    await message.answer(text)

@dp.message(Command('custom'))
async def cmd_custom(message: Message):
    await message.answer("👋 Hello! This is a custom command.")

@dp.message(Command('info'))
async def cmd_info(message: Message):
    await message.answer("ℹ️ I am a simple bot built with Aiogram.")

@dp.message(Command('echo'))
async def cmd_echo(message: Message):
    text = message.text.replace('/echo', '').strip()
    await message.answer(f'🔁 You said: {text}' if text else "Please provide text after /echo.")

@dp.message(Command('buttons'))
async def cmd_buttons(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Google", url='https://www.google.com')],
            [InlineKeyboardButton(text="💻 GitHub", url='https://github.com')],
            [
                InlineKeyboardButton(text="Say Hello", callback_data='say_hello'),
                InlineKeyboardButton(text="Info", callback_data='get_info'),
            ]
        ]
    )
    await message.answer("Choose an option:", reply_markup=keyboard)

@dp.callback_query(F.data == 'say_hello')
async def cb_hello(callback: CallbackQuery):
    await callback.message.edit_text("👋 Hello there!")
    await callback.answer()

@dp.callback_query(F.data == 'get_info')
async def cb_info(callback: CallbackQuery):
    await callback.message.edit_text("🤖 This bot is for demo purposes.")
    await callback.answer()

@dp.message(Command('begin'))
async def begin(message: Message, state: FSMContext):
    await message.answer("📝 Great! What is your <b>name</b>?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name_input(message: Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await cancel(message, state)
        return
    await state.update_data(name=message.text)
    await message.answer("Nice to meet you! What is your <b>email</b>?")
    await state.set_state(Form.email)

@dp.message(Form.email)
async def email_input(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(f"📧 You said your email is: <b>{message.text}</b>\nIs this correct? (Yes/No)")
    await state.set_state(Form.confirm)

@dp.message(Form.confirm)
async def confirm_input(message: Message, state: FSMContext):
    text = message.text.lower()
    if text == "yes":
        data = await state.get_data()
        await message.answer(f"✅ Thank you <b>{data['name']}</b>! Your info has been recorded.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif text == "no":
        await message.answer("❌ Let's start over. Type /begin to restart.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer("⚠️ Please respond with 'Yes' or 'No'.")

@dp.message(Command('cancel'))
async def cancel(message: Message, state: FSMContext):
    await message.answer("🚫 Conversation canceled. Type /start to restart")
    await state.clear()

@dp.callback_query(F.data == "submit_review")
async def start_review(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Please enter your <b>name</b>:")
    await state.set_state(ReviewForm.name)
    await callback.answer()

@dp.message(ReviewForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📧 Please enter your <b>email</b>:")
    await state.set_state(ReviewForm.email)

@dp.message(ReviewForm.email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("⭐ Please rate us (1-5):")
    await state.set_state(ReviewForm.rating)

@dp.message(ReviewForm.rating)
async def process_rating(message: Message, state: FSMContext):
    rating_text = message.text.strip()
    if not rating_text.isdigit() or not (1 <= int(rating_text) <= 5):
        await message.answer("⚠️ Please enter a valid rating between 1 and 5.")
        return

    await state.update_data(rating=int(rating_text))
    await message.answer("💬 Optional: Please enter your comment (or type 'skip' to continue):")
    await state.set_state(ReviewForm.comment)

@dp.message(ReviewForm.comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text if message.text.lower() != 'skip' else ''
    await state.update_data(comment=comment)

    data = await state.get_data()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Submit", callback_data="submit_review_confirm"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_review")
        ]
    ])

    summary = (
        f"<b>Please confirm your review:</b>\n\n"
        f"👤 Name: <b>{data['name']}</b>\n"
        f"📧 Email: <b>{data['email']}</b>\n"
        f"⭐ Rating: <b>{data['rating']}/5</b>\n"
        f"💬 Comment: <i>{comment or 'No comment'}</i>"
    )
    await message.answer(summary, reply_markup=kb)

@dp.callback_query(F.data == "submit_review_confirm")
async def submit_review(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id

    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reviews (user_id, name, email, rating, comment)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, data['name'], data['email'], data['rating'], data['comment']))
    conn.commit()
    conn.close()

    await callback.message.edit_text("✅ Thank you! Your review has been submitted.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "cancel_review")
async def cancel_review(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Review canceled.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "review")
async def review(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 View All Reviews", callback_data="view_all_reviews")],
        [InlineKeyboardButton(text="👤 My Reviews", callback_data="my_reviews")]
    ])
    await callback.message.edit_text("📋 Review Menu:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "view_all_reviews")
async def view_all_reviews(callback: CallbackQuery):
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, rating, comment FROM reviews')
    reviews = cursor.fetchall()
    conn.close()

    if not reviews:
        await callback.message.edit_text("No reviews found.")
        await callback.answer()
        return

    response = "<b>📋 All Reviews:</b>\n\n"
    for idx, (name, email, rating, comment) in enumerate(reviews, 1):
        response += (
            f"{idx}. 👤 <b>{name}</b>\n"
            f"   📧 <i>{email}</i>\n"
            f"   ⭐ <b>{rating}/5</b>\n"
        )
        if comment:
            response += f"   💬 {comment}\n"
        response += "\n"

    await callback.message.edit_text(response)
    await callback.answer()

@dp.callback_query(F.data == 'my_reviews')
async def my_reviews(callback: CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, rating, comment FROM reviews WHERE user_id = ?', (user_id,))
    reviews = cursor.fetchall()
    conn.close()

    if not reviews:
        await callback.message.answer(
            "❌ You haven't submitted any reviews yet.\n\n"
            "To submit your review, press the 'Submit Review' button below.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Submit Review", callback_data='submit_review')]
                ]
            )
        )
    else:
        response = "<b>📝 Your Reviews:</b>\n\n"
        for idx, (name, email, rating, comment) in enumerate(reviews, 1): 
            response += (
                f"{idx}. 👤 <b>{name}</b>\n"
                f"   📧 <i>{email}</i>\n"
                f"   ⭐ <b>{rating}/5</b>\n"
            )
            if comment:
                response += f"   💬 {comment}\n"
            response += "\n"
        await callback.message.answer(response)

    await callback.answer()


def handle_response(text: str) -> str:
    text = text.lower()
    if 'hello' in text:
        return "Hello! How can I help you today?"
    if 'how are you' in text:
        return "I'm doing great!"
    if 'python' in text:
        return "🐍 Python is awesome!"
    return "🤔 I didn't understand that."

async def main():
    init_db()
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")


