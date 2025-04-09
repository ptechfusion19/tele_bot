import logging
from typing import final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler


TOKEN: final = '6482255236:AAEScgnZK3hsIpOQ-sxlHGAxK1H5R0e3UXI'
BOT_USERNAME: final = '@rewarddistributionbot'

COMMANDS_HELP = {
    '/start': 'Starts the bot and gives a welcome message.',
    '/help': 'Shows the list of available commands and how to use them.',
    '/custom': 'Executes a custom command. You can extend this with functionality.',
    '/info': 'Provides information about the bot.',
    '/echo': 'Echoes the message you send to the bot.',
}


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


NAME, EMAIL, CONFIRMATION = range(3)
user_data = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am your bot. You can talk to me here.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "Here are the commands I support:\n\n"
    for command, description in COMMANDS_HELP.items():
        help_text += f"{command}: {description}\n"
    await update.message.reply_text(help_text)


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! This is a custom command.')


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am a simple Telegram bot. I can respond to predefined commands and messages.')


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    echo_message = user_message.replace('/echo', '').strip()
    if echo_message:
        await update.message.reply_text(f'You said: {echo_message}')
    else:
        await update.message.reply_text('Please provide a message to echo.')


def handle_response(text: str) -> str:
    processed: str = text.lower()
    
    if 'hello' in processed:
        return 'Hello! How can I assist you today?'
    
    if 'how are you' in processed:
        return 'I am good!'
    
    if 'python' in processed:
        return 'Python is a great programming language!'
    
    return 'I am not sure how to respond to that.'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    print(f"User({update.effective_user.id}) in {message_type} sent: {text}")
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Great! What is your name?")
    return NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.message.from_user.id] = {'name': update.message.text}  # Store the name
    await update.message.reply_text(f"Hello, {update.message.text}! What is your email address?")
    return EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.message.from_user.id]['email'] = update.message.text  # Store the email
    await update.message.reply_text(f"Got it! You said your email is {update.message.text}. Is everything correct? (Yes/No)")
    return CONFIRMATION

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.lower()

    if response == 'yes':
        
        user_info = user_data[update.message.from_user.id]
        await update.message.reply_text(f"Thank you {user_info['name']}! Your information has been recorded.")
        del user_data[update.message.from_user.id]  # Clear the stored user data
        return ConversationHandler.END
    elif response == 'no':
        await update.message.reply_text("Let's start over. Type /begin to begin again.")
        return ConversationHandler.END
    else:
        
        await update.message.reply_text("Please respond with 'Yes' or 'No'.")
        return CONFIRMATION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("The conversation has been canceled. You can type /begin to start again.")
    return ConversationHandler.END

if __name__ == '__main__':
    
    app = Application.builder().token(TOKEN).build()


    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('echo', echo_command))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    
    app.add_error_handler(error)

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('begin', start_conversation)],  
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.Command(), ask_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.Command(), ask_email)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.Command(), handle_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],  
    )
    
    # Add conversation handler
    app.add_handler(conversation_handler)

    # Start polling for updates
    print('Bot started!')
    app.run_polling(poll_interval=1)
