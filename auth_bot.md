# Documentation for Telegram Bot with Admin and User Roles

## Overview

This bot allows both users and admins to interact with the system in different ways. Users can submit reviews, while admins have access to more sensitive features like managing users, viewing all reviews, and setting roles. The bot uses the Aiogram framework, SQLite for storing data, and FSM (Finite State Machine) for handling user input in various states.

## Requirements

- **Python 3.7+**
- **Aiogram**: for creating the Telegram bot and handling interactions.
- **SQLite**: for storing user roles, credentials, and reviews.
- **FSM (Finite State Machine)**: for managing complex user flows.

## File Structure

- **roles.db**: SQLite database for storing user credentials, roles, and reviews.
- **main.py**: The main Python file that contains all the logic for the Telegram bot.

---

## Key Components

### 1. **Bot Initialization and States**

- The bot is initialized using Aiogram's `Dispatcher` and `Bot` classes. `dp` is used to handle incoming messages and callbacks.
- FSM states are defined for user inputs, like adding users, reviewing, and resetting passwords. These states control the flow of user input and ensure the bot interacts with the user in a structured way.

### 2. **Database Setup (`roles.db`)**

- **Credentials**: Stores usernames, passwords, and roles of users (admin or regular user).
- **Reviews**: Stores reviews submitted by users, which include the name, email, rating, and comment.
- The SQLite database is queried when actions like viewing reviews, managing users, or submitting a review are triggered.

### 3. **User Authentication and Roles**

- **Admin and User Roles**: The bot distinguishes between users and admins based on the `role` column in the `credentials` table.
- **Admin-only commands**: Admin users have access to commands like `/set_role`, `/view_users`, `/delete_user`, etc.
- **Role Assignment**: Role is set using the `set_user_role()` function. The role is stored in the FSM context and database.

### 4. **Handlers and Commands**

#### 4.1 **Inline Keyboard Markup**

The `InlineKeyboardMarkup` is used to create dynamic inline buttons based on the user's role. Admins see additional options like "🔐 Admin Panel," while regular users are shown limited commands. This is controlled by the `markup` function that generates buttons based on role.

#### 4.2 **Command Handlers**

- `/help`: Displays available commands based on the user's role.
- `/whoami`: Returns the user's role (admin or user).
- `/open_user`: Logs the user in as a regular user.
- `/logout`: Logs the user out and sets their role to regular user.
- `/submit_review`: Allows users to submit reviews, and the process is managed using FSM states like `SubmitReviewFSM.name`, `SubmitReviewFSM.email`, etc.
- `/view_reviews`: Allows both admins and users to view reviews based on role. Admins can view all reviews, while regular users can only see their own.
- `/add_user`: Admin-only command to add new users.
- `/delete_user`: Admin-only command to delete existing users.
- `/set_role`: Admin-only command to set user roles.
- `/view_users`: Admin-only command to view all users and their roles.

#### 4.3 **FSM States and Data Flow**

- **Add User Flow**: Admins can add users by specifying their username, password, and role (`/add_user`).
- **Submit Review Flow**: Users are prompted to submit reviews, which include their name, email, rating, and comment. The review is then stored in the database.
- **View Reviews Flow**: Displays all reviews, with formatting that distinguishes between admin and user views.
- **Delete User Flow**: Admins can delete users by specifying their username.
- **Set Role Flow**: Admins can assign roles to users.

#### 4.4 **Error Handling and Permission Checks**

- Before performing certain actions (like viewing users or changing roles), the bot checks whether the user is an admin. If not, the bot sends a "permission denied" message.
- Error handling ensures that users don't try to submit invalid data (like a rating outside the 1-5 range).

---

## Code Breakdown

### 1. **Bot Setup and Main Handler**

```python
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Function to start polling the bot
async def main():
    init_db()
    print("🤖 Bot is running...")
    await dp.start_polling(bot)
```

- Initializes the bot and dispatcher with the given token.
- The `main()` function initializes the database and starts the polling process for listening to user messages.

### 2. **Database Initialization**

```python
def init_db():
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    # Create tables for credentials and reviews
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (
                     id INTEGER PRIMARY KEY,
                     username TEXT UNIQUE,
                     password TEXT,
                     role TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
                     id INTEGER PRIMARY KEY,
                     user_id INTEGER,
                     name TEXT,
                     email TEXT,
                     rating INTEGER,
                     comment TEXT,
                     FOREIGN KEY(user_id) REFERENCES credentials(id)
                 )''')
    conn.commit()
    conn.close()
```

- **init_db()** sets up the SQLite database with two tables: `credentials` (for user info) and `reviews` (for storing user reviews).
  
### 3. **Command Handlers**

#### **/help**

```python
@dp.callback_query(F.data == "/help")
async def cmd_help_callback(callback: CallbackQuery):
    role = get_user_role(callback.from_user.id)
    allowed = [cmd for cmd, desc in COMMANDS_HELP.items() if role == ADMIN_ROLE or cmd not in admin_only_commands]
    help_text = "<b>Available Commands:</b>

"
    help_text += '
'.join(f"{cmd}: {COMMANDS_HELP[cmd]}" for cmd in allowed)
    await callback.message.answer(help_text)
```

- Displays available commands to the user. Admins see all commands, while regular users only see commands available to them.

#### **/submit_review**

```python
@dp.callback_query(F.data == "/submit_review")
async def submit_review_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please provide your name:")
    await state.set_state(SubmitReviewFSM.name)
    await callback.answer()
```

- Starts the review submission process by prompting the user for their name, email, rating, and comment. The FSM is used to handle each step of the process.

---

## Security and Permissions

- **Admin-Only Commands**: The bot ensures that only admins can access sensitive commands such as `/set_role`, `/view_users`, and `/delete_user`. These permissions are checked by verifying the user’s role before executing the corresponding commands.
  
- **FSM Context**: User input is managed through the FSM context, which stores the state of the user’s interaction. This ensures the bot interacts with the user step-by-step.

---

## Conclusion

This bot is a multi-functional Telegram bot that offers role-based access to commands, allowing for both user and admin interactions. It supports FSM for complex flows and SQLite for persistent data storage. The structure ensures separation of concerns, with user roles and permissions strictly enforced, making the bot both efficient and secure.
