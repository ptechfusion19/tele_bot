# import logging
# from typing import final

# from telegram import (
#     Update,
#     ReplyKeyboardMarkup,
#     ReplyKeyboardRemove,
#     InlineKeyboardButton,
#     InlineKeyboardMarkup,
# )

# from telegram.ext import (
#     Application,
#     CommandHandler,
#     MessageHandler,
#     CallbackQueryHandler,
#     filters,
#     ContextTypes,
#     ConversationHandler,
# )

# TOKEN: final = '8016112194:AAEYKqbIHjIHnqd-T77JktYG2C8vJVCsqHE'
# BOT_USERNAME: final = '@differnet123bot_bot'

# COMMANDS_HELP = {
#     '/start': 'Starts the bot and gives a welcome message.',
#     '/help': 'Shows the list of available commands and how to use them.',
#     '/custom': 'Executes a custom command. You can extend this with functionality.',
#     '/info': 'Provides information about the bot.',
#     '/echo': 'Echoes the message you send to the bot.',
#     '/buttons': 'Shows inline buttons and links.',
#     '/begin': 'Starts the conversation to collect user info.',
#     '/cancel': 'Cancels the current conversation.',
#     '/google': 'Sends a link to Google.',
#     '/github': 'Sends a link to GitHub.',
#     '/remove': 'Removes the custom keyboard.',
# }

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# NAME, EMAIL, CONFIRMATION = range(3)
# user_data = {}


# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     welcome_message = (
#         "*Welcome!* 👋\n\n"
#         "I'm your assistant bot.\n"
#         "Type /help to see what I can do."
#     )
#     reply_keyboard = [
#         ['/help', '/info'],
#         ['/custom', '/echo'],
#         ['/buttons', '/begin'],
#         ['/cancel', '/google'],
#         ['/github', '/remove']
#     ]
#     await update.message.reply_text(
#         welcome_message,
#         parse_mode='Markdown',
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard, resize_keyboard=True, one_time_keyboard=False
#         )
#     )

# async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     help_text = "*Here are the commands I support:*\n\n"
#     for command, description in COMMANDS_HELP.items():
#         help_text += f"{command}: {description}\n"
#     await update.message.reply_text(help_text, parse_mode='Markdown')

# async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text('👋 Hello! This is a custom command.')

# async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         'ℹ️ I am a simple Telegram bot. I can respond to predefined commands and messages.'
#     )

# async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_message = update.message.text
#     echo_message = user_message.replace('/echo', '').strip()
#     if echo_message:
#         await update.message.reply_text(f'🔁 You said: {echo_message}')
#     else:
#         await update.message.reply_text('Please provide a message to echo.')

# async def google_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("🌐 [Google](https://www.google.com)", parse_mode='Markdown')

# async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("💻 [GitHub](https://github.com)", parse_mode='Markdown')

# async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "🧼 Removed custom keyboard. Type /start to get it back.",
#         reply_markup=ReplyKeyboardRemove()
#     )

# async def buttons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [
#         [InlineKeyboardButton("🌐 Google", url='https://www.google.com')],
#         [InlineKeyboardButton("💻 GitHub", url='https://github.com')],
#         [
#             InlineKeyboardButton("Say Hello", callback_data='say_hello'),
#             InlineKeyboardButton("Info", callback_data='get_info'),
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

# async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#     if query.data == 'say_hello':
#         await query.edit_message_text("👋 Hello there!")
#     elif query.data == 'get_info':
#         await query.edit_message_text("🤖 This bot is for demo purposes.")


# async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("📝 Great! What is your *name*?", parse_mode='Markdown')
#     return NAME

# async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_data[update.message.from_user.id] = {'name': update.message.text}
#     await update.message.reply_text(f"Nice to meet you, {update.message.text}! What's your *email*?", parse_mode='Markdown')
#     return EMAIL

# async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_data[update.message.from_user.id]['email'] = update.message.text
#     await update.message.reply_text(
#         f"Got it! 📧 You said your email is: *{update.message.text}*.\nIs this correct? (Yes/No)",
#         parse_mode='Markdown'
#     )
#     return CONFIRMATION

# async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     response = update.message.text.lower()
#     if response == 'yes':
#         user_info = user_data[update.message.from_user.id]
#         await update.message.reply_text(
#             f"✅ Thank you *{user_info['name']}*! Your info has been recorded.",
#             parse_mode='Markdown',
#             reply_markup=ReplyKeyboardRemove()
#         )
#         del user_data[update.message.from_user.id]
#         return ConversationHandler.END
#     elif response == 'no':
#         await update.message.reply_text(
#             "❌ Let's start over. Type /begin to start again.",
#             reply_markup=ReplyKeyboardRemove()
#         )
#         return ConversationHandler.END
#     else:
#         await update.message.reply_text("⚠️ Please respond with 'Yes' or 'No'.")
#         return CONFIRMATION

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         "🚫 The conversation has been canceled. You can type /begin to start again.",
#         reply_markup=ReplyKeyboardRemove()
#     )
#     return ConversationHandler.END



# def handle_response(text: str) -> str:
#     processed = text.lower()
#     if 'hello' in processed:
#         return 'Hello! How can I assist you today?'
#     if 'how are you' in processed:
#         return 'I am good!'
#     if 'python' in processed:
#         return '🐍 Python is a great programming language!'
#     return '🤔 I am not sure how to respond to that.'

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     message_type = update.message.chat.type
#     text = update.message.text
#     print(f"User({update.effective_user.id}) in {message_type} sent: {text}")
#     if message_type == 'group':
#         if BOT_USERNAME in text:
#             new_text = text.replace(BOT_USERNAME, '').strip()
#             response = handle_response(new_text)
#         else:
#             return
#     else:
#         response = handle_response(text)
#     print('Bot:', response)
#     await update.message.reply_text(response)

# async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(f'Update {update} caused error {context.error}')


# if __name__ == '__main__':
#     app = Application.builder().token(TOKEN).build()

#     app.add_handler(CommandHandler('start', start_command))
#     app.add_handler(CommandHandler('help', help_command))
#     app.add_handler(CommandHandler('custom', custom_command))
#     app.add_handler(CommandHandler('info', info_command))
#     app.add_handler(CommandHandler('echo', echo_command))
#     app.add_handler(CommandHandler('buttons', buttons_command))
#     app.add_handler(CommandHandler('google', google_command))
#     app.add_handler(CommandHandler('github', github_command))
#     app.add_handler(CommandHandler('remove', remove_keyboard))
#     app.add_handler(CommandHandler('cancel', cancel))

#     app.add_handler(CallbackQueryHandler(button_callback))

#     conversation_handler = ConversationHandler(
#         entry_points=[CommandHandler('begin', start_conversation)],
#         states={
#             NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
#             EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
#             CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)],
#         },
#         fallbacks=[CommandHandler('cancel', cancel)],
#     )
#     app.add_handler(conversation_handler)

#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#     app.add_error_handler(error)

#     print("Bot started!")
#     app.run_polling(poll_interval=1)


#-----------------------using aiogram---------------------


import asyncio
import logging
import sqlite3
from typing import Final

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage

# Bot token and username
TOKEN: Final = '8016112194:AAEYKqbIHjIHnqd-T77JktYG2C8vJVCsqHE'.strip()
BOT_USERNAME: Final = '@differnet123bot_bot'

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Command help list
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

# FSM for form
class Form(StatesGroup):
    name = State()
    email = State()
    confirm = State()

class ReviewForm(StatesGroup):
    name = State()
    rating = State()
    comment = State()

# Setup SQLite DB for reviews
def init_db():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            rating INTEGER,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()

# /start command
@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='/help'), KeyboardButton(text='/info')],
            [KeyboardButton(text='/custom'), KeyboardButton(text='/echo')],
            [KeyboardButton(text='/buttons'), KeyboardButton(text='/begin')],
            [KeyboardButton(text='/cancel'), KeyboardButton(text='/review')],
            [KeyboardButton(text='/view_reviews'), KeyboardButton(text='/remove')],
        ],
        resize_keyboard=True
    )
    await message.answer(
        "<b>Welcome!</b> 👋\n\nI'm your assistant bot.\nType /help to see what I can do.",
        reply_markup=kb
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

@dp.message(Command('remove'))
async def cmd_remove(message: Message):
    await message.answer("🧼 Removed keyboard. Type /start to get it back.", reply_markup=ReplyKeyboardRemove())

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

# FSM form: name -> email -> confirm
@dp.message(Command('begin'))
async def begin(message: Message, state: FSMContext):
    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Cancel')]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("📝 Great! What is your <b>name</b>?", reply_markup=cancel_kb)
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name_input(message: Message, state: FSMContext):
    if message.text.lower() == 'cancel':
        await cancel(message, state)
        return
    await state.update_data(name=message.text)
    await message.answer("Nice to meet you! What is your <b>email</b>?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Cancel')]],
        resize_keyboard=True,
        one_time_keyboard=True
    ))
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
    await message.answer("🚫 Conversation canceled.", reply_markup=ReplyKeyboardRemove())
    await state.clear()

# Review form start
@dp.message(Command('review'))
async def start_review(message: Message, state: FSMContext):
    await message.answer("📝 Please enter your <b>name</b> for the review:")
    await state.set_state(ReviewForm.name)

@dp.message(ReviewForm.name)
async def process_review_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🔢 Please rate us (1-5):")
    await state.set_state(ReviewForm.rating)

@dp.message(ReviewForm.rating)
async def process_review_rating(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (1 <= int(message.text) <= 5):
        await message.answer("Rating must be a number between 1 and 5. Try again:")
        return
    await state.update_data(rating=int(message.text))
    await message.answer("💬 Any comments? (Type 'skip' to leave blank):")
    await state.set_state(ReviewForm.comment)

@dp.message(ReviewForm.comment)
async def process_review_comment(message: Message, state: FSMContext):
    comment = message.text if message.text.lower() != 'skip' else ''
    await state.update_data(comment=comment)

    data = await state.get_data()

    # Inline keyboard for Submit and Cancel
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Submit", callback_data="submit_review"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_review")
        ]
    ])

    summary = (
        f"<b>Please confirm your review:</b>\n\n"
        f"👤 Name: <b>{data['name']}</b>\n"
        f"⭐ Rating: <b>{data['rating']}/5</b>\n"
        f"💬 Comment: <i>{comment or 'No comment'}</i>"
    )
    await message.answer(summary, reply_markup=kb)
    @dp.callback_query(F.data == "submit_review")
    async def submit_review(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        user_id = callback.from_user.id

        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reviews (user_id, name, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, data['name'], data['rating'], data['comment']))
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

@dp.message(Command('view_reviews'))
async def view_reviews(message: Message):
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, rating, comment FROM reviews')
    reviews = cursor.fetchall()
    conn.close()

    if not reviews:
        await message.answer("No reviews found.")
        return

    response = "<b>📋 Reviews:</b>\n\n"
    for idx, (name, rating, comment) in enumerate(reviews, 1):
        response += f"{idx}. <b>{name}</b> rated <b>{rating}/5</b>\n"
        if comment:
            response += f"   💬 {comment}\n"
        response += "\n"

    await message.answer(response)

# Fallback text handler
def handle_response(text: str) -> str:
    text = text.lower()
    if 'hello' in text:
        return "Hello! How can I help you today?"
    if 'how are you' in text:
        return "I'm doing great!"
    if 'python' in text:
        return "🐍 Python is awesome!"
    return "🤔 I didn't understand that."

@dp.message()
async def fallback(message: Message):
    response = handle_response(message.text)
    await message.answer(response)

# Start bot
async def main():
    init_db()
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")


