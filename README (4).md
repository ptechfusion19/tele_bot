
# 🤖 Tele_Bot

**Tele-Bot** is a feature-rich Telegram bot built with [Aiogram v3](https://docs.aiogram.dev/en/dev-3.x/) in Python. It includes user authentication, admin/user role management, FSM-based review submissions, and support for sending and receiving media files — all in a single-file architecture with SQLite for storage.

---

## ✨ Features

- 🔐 **Login system** with inline buttons and stored credentials
- 🧑‍💼 **Role-based access** (Admin/User)
- 📋 **FSM-based review submission** (name, email, rating, comment)
- 🗂️ **Review viewing** (admin-only)
- 👤 **User management**:
  - Add user
  - Delete user
  - Reset password
  - Set role
- 📸 **Send media files**: photo, video, audio, and documents
- 🎛️ FSM auto-cancellation on new command or callback
- 💾 SQLite-based persistent storage

---

## 🛠 Installation

### Prerequisites
Python 3.7 or higher, Aiogram library, and SQLite
Install the Aiogram library using pip:

```bash
pip install aiogram
```

## **Set your bot token in `config.py`:**

   Create a file named `config.py`:

   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ADMIN_ROLE = "admin"
   USER_ROLE = "user"
   ```

---

## 🚀 Running the Bot

To run the bot with polling:

```bash
python bot.py
```

To delete the webhook (optional):

```bash
python delete_webhook.py
```

---

## 📂 Project Structure

```text
tele-bot/
├── bot.py              # Main entry point
├── database.py         # SQLite database logic and user management
├── delete_webhook.py   # Removes existing Telegram webhook
├── handlers/           # FSM flows and feature-specific handlers
│   ├── auth.py
│   ├── admin.py
│   ├── user.py
│   ├── review.py
│   └── media.py
├── middlewares/
│   └── CancelFSMOnNewEventMiddleware.py
├── config.py           # Configuration variables (token, roles)
└── roles.db            # SQLite database (auto-created)
```

---

## 🧪 Default Credentials

- **Admin:** `admin123` / `adminpass`
- **User:** `user123` / `userpass`

---
## 📜 Usage Instructions

To set up the bot, ensure you have all dependencies installed and the required environment variables set. Follow the instructions in the `config.py` file
before running `bot.py`, ensure you have your Telegram bot token and any necessary configuration set up correctly.

## 🙌 Credits

Built with 💙 using [Aiogram v3].
