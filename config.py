# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot token and username
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = '@differnet123bot_bot'

# Role constants
ADMIN_ROLE = "admin"
USER_ROLE = "user"

# Help descriptions for all commands
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
