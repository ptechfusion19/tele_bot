# Telegram Bot with Role-Based Access and FSM (Aiogram v3)

This bot uses the Aiogram v3 framework with full role-based access (admin/user), login authentication, command filtering by role, and FSM (Finite State Machine) flows. It stores users and credentials in a SQLite database and supports media uploads, custom buttons, and more.

## 🔧 Features

- Role management (admin / user)
- Login system using username and password
- FSM-based input collection for commands
- Command restriction based on user roles
- Inline buttons for login and user access
- Persistent user and credential storage using SQLite
- Cancel FSM automatically on new command or callback
- Environment variable-based bot token loading

## 📦 Requirements

- Python 3.8+
- Aiogram v3
- Python-dotenv
- SQLite3

Install dependencies:

```bash
pip install aiogram python-dotenv
```

## 📁 Environment Setup

Create a `.env` file in the root directory:

```env
BOT_TOKEN=your_telegram_bot_token
```

## 🧠 Commands Overview

| Command           | Description |
|-------------------|-------------|
| `/start`          | Start the bot and show login options |
| `/help`           | Show available commands based on role |
| `/login`          | Login with username/password |
| `/logout`         | Logout and revert to user role |
| `/open_user`      | Continue as user without credentials |
| `/whoami`         | Check your current role |
| `/add_user`       | Add a new user (admin only) |
| `/set_role`       | Change user role (admin only) |
| `/delete_user`    | Delete a user (admin only) |
| `/reset_password` | Reset a user's password (admin only) |
| `/view_users`     | List all users and their roles (admin only) |

## 🗃️ Default Credentials

| Username  | Password   | Role  |
|-----------|------------|-------|
| admin123  | adminpass  | admin |
| user123   | userpass   | user  |

## 📚 Code Structure

- **Bot initialization:** Uses `dotenv` and creates required SQLite tables.
- **FSM states:** Handles username/password/role inputs.
- **Middleware:** Cancels FSM flows when any command or callback is triggered.
- **Command filtering:** Commands like `/add_user`, `/set_role` are only available to admins.
- **Inline login buttons:** Shown on `/start` with "Login" and "Continue as User".

## 🧩 FSM Classes

```python
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
```

## 🧠 Middleware

Cancels any ongoing FSM input when a new command or callback query is triggered:

```python
class CancelFSMOnNewEventMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state: FSMContext = data.get("state")
        if state and await state.get_state():
            if isinstance(event, Message) and event.text and event.text.startswith('/'):
                await state.clear()
            elif isinstance(event, CallbackQuery):
                await state.clear()
        return await handler(event, data)
```

## 🏁 Entry Point

```python
async def main():
    init_db()
    print("🤖 Bot is running...")
    await dp.start_polling(bot)
```

---

