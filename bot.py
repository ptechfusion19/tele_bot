import logging
from typing import final

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

TOKEN: final = '8016112194:AAEYKqbIHjIHnqd-T77JktYG2C8vJVCsqHE'
BOT_USERNAME: final = '@differnet123bot_bot'

COMMANDS_HELP = {
    '/start': 'Starts the bot and gives a welcome message.',
    '/help': 'Shows the list of available commands and how to use them.',
    '/custom': 'Executes a custom command. You can extend this with functionality.',
    '/info': 'Provides information about the bot.',
    '/echo': 'Echoes the message you send to the bot.',
    '/buttons': 'Shows inline buttons and links.',
    '/begin': 'Starts the conversation to collect user info.',
    '/cancel': 'Cancels the current conversation.',
    '/google': 'Sends a link to Google.',
    '/github': 'Sends a link to GitHub.',
    '/remove': 'Removes the custom keyboard.',
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

NAME, EMAIL, CONFIRMATION = range(3)
user_data = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "*Welcome!* 👋\n\n"
        "I'm your assistant bot.\n"
        "Type /help to see what I can do."
    )
    reply_keyboard = [
        ['/help', '/info'],
        ['/custom', '/echo'],
        ['/buttons', '/begin'],
        ['/cancel', '/google'],
        ['/github', '/remove']
    ]
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=False
        )
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "*Here are the commands I support:*\n\n"
    for command, description in COMMANDS_HELP.items():
        help_text += f"{command}: {description}\n"
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('👋 Hello! This is a custom command.')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'ℹ️ I am a simple Telegram bot. I can respond to predefined commands and messages.'
    )

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    echo_message = user_message.replace('/echo', '').strip()
    if echo_message:
        await update.message.reply_text(f'🔁 You said: {echo_message}')
    else:
        await update.message.reply_text('Please provide a message to echo.')

async def google_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 [Google](https://www.google.com)", parse_mode='Markdown')

async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 [GitHub](https://github.com)", parse_mode='Markdown')

async def remove_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧼 Removed custom keyboard. Type /start to get it back.",
        reply_markup=ReplyKeyboardRemove()
    )

async def buttons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 Google", url='https://www.google.com')],
        [InlineKeyboardButton("💻 GitHub", url='https://github.com')],
        [
            InlineKeyboardButton("Say Hello", callback_data='say_hello'),
            InlineKeyboardButton("Info", callback_data='get_info'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'say_hello':
        await query.edit_message_text("👋 Hello there!")
    elif query.data == 'get_info':
        await query.edit_message_text("🤖 This bot is for demo purposes.")


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Great! What is your *name*?", parse_mode='Markdown')
    return NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.message.from_user.id] = {'name': update.message.text}
    await update.message.reply_text(f"Nice to meet you, {update.message.text}! What's your *email*?", parse_mode='Markdown')
    return EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.message.from_user.id]['email'] = update.message.text
    await update.message.reply_text(
        f"Got it! 📧 You said your email is: *{update.message.text}*.\nIs this correct? (Yes/No)",
        parse_mode='Markdown'
    )
    return CONFIRMATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.lower()
    if response == 'yes':
        user_info = user_data[update.message.from_user.id]
        await update.message.reply_text(
            f"✅ Thank you *{user_info['name']}*! Your info has been recorded.",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        del user_data[update.message.from_user.id]
        return ConversationHandler.END
    elif response == 'no':
        await update.message.reply_text(
            "❌ Let's start over. Type /begin to start again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("⚠️ Please respond with 'Yes' or 'No'.")
        return CONFIRMATION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚫 The conversation has been canceled. You can type /begin to start again.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END



def handle_response(text: str) -> str:
    processed = text.lower()
    if 'hello' in processed:
        return 'Hello! How can I assist you today?'
    if 'how are you' in processed:
        return 'I am good!'
    if 'python' in processed:
        return '🐍 Python is a great programming language!'
    return '🤔 I am not sure how to respond to that.'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    print(f"User({update.effective_user.id}) in {message_type} sent: {text}")
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('echo', echo_command))
    app.add_handler(CommandHandler('buttons', buttons_command))
    app.add_handler(CommandHandler('google', google_command))
    app.add_handler(CommandHandler('github', github_command))
    app.add_handler(CommandHandler('remove', remove_keyboard))
    app.add_handler(CommandHandler('cancel', cancel))

    app.add_handler(CallbackQueryHandler(button_callback))

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('begin', start_conversation)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conversation_handler)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error)

    print("Bot started!")
    app.run_polling(poll_interval=1)
