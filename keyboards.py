from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import COMMANDS_HELP, ADMIN_ROLE

def build_start_keyboard():
    """Create an inline keyboard with login and guest access buttons."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔐 Login", callback_data="login")
        ],
        [
            InlineKeyboardButton(text="👤 Continue as User", callback_data="open_user")
        ]
    ])

def build_command_keyboard(role: str):
    """Build a command keyboard layout depending on user role."""
    user_buttons = []
    admin_buttons = []

    # Separate user and admin commands
    for cmd, desc in COMMANDS_HELP.items():
        btn = InlineKeyboardButton(text=cmd, callback_data=cmd)
        if role == ADMIN_ROLE or cmd not in [
            "/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"
        ]:
            if cmd in [
                "/add_user", "/set_role", "/view_users", "/delete_user", "/reset_password"
            ]:
                admin_buttons.append(btn)
            else:
                user_buttons.append(btn)

    # Arrange buttons in pairs for better layout
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        *[user_buttons[i:i + 2] for i in range(0, len(user_buttons), 2)]
    ])

    if admin_buttons:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="🔐 Admin Panel", callback_data="ignore_admin_title")]
        )
        keyboard.inline_keyboard.extend(
            [admin_buttons[i:i + 2] for i in range(0, len(admin_buttons), 2)]
        )

    return keyboard
