import sqlite3
from config import ADMIN_ROLE, USER_ROLE

# Default credentials loaded at startup
CREDENTIALS = {
    "admin123": {"password": "adminpass", "role": ADMIN_ROLE},
    "user123": {"password": "userpass", "role": USER_ROLE},
}

def init_db():
    """Initialize database and tables if not exist."""
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        role TEXT DEFAULT 'user'
    )''')

    # Create credentials table
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )''')

    # Create reviews table (linked to users by Telegram user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        email TEXT,
        rating INTEGER,
        comment TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )''')

    # Insert default credentials
    for username, data in CREDENTIALS.items():
        c.execute("INSERT OR IGNORE INTO credentials (username, password, role) VALUES (?, ?, ?)",
                  (username, data["password"], data["role"]))

    conn.commit()
    conn.close()

def get_user_role(user_id: int):
    """Fetch the user's role or assign default if missing."""
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if not result:
        set_user_role(user_id, USER_ROLE)
        return USER_ROLE
    return result[0]

def set_user_role(user_id: int, role: str):
    """Insert or update a user's role."""
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()
