import sqlite3
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "expense.db")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        daily_limit INTEGER DEFAULT 0,
        weekly_limit INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        category TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER
    )
    """)

    conn.commit()
    conn.close()


def register_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )

    conn.commit()
    conn.close()


def add_expense(user_id, amount, category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (user_id, amount, category, created_at) VALUES (?, ?, ?, ?)",
        (user_id, amount, category, str(date.today()))
    )

    conn.commit()
    conn.close()


def set_salary(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM salary WHERE user_id=?", (user_id,))
    cursor.execute("INSERT INTO salary (user_id, amount) VALUES (?, ?)", (user_id, amount))

    cursor.execute("DELETE FROM expenses WHERE user_id=?", (user_id,))

    conn.commit()
    conn.close()


def set_limits(user_id, daily, weekly):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET daily_limit=?, weekly_limit=? WHERE user_id=?",
        (daily, weekly, user_id)
    )

    conn.commit()
    conn.close()


def get_limits(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT daily_limit, weekly_limit FROM users WHERE user_id=?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result if result else (0, 0)


def get_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    total = cursor.fetchone()[0] or 0

    cursor.execute("SELECT amount FROM salary WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,))
    salary = cursor.fetchone()
    salary = salary[0] if salary else 0

    conn.close()
    return salary - total


def get_all_expenses(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT amount, category, created_at FROM expenses WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchall()
    conn.close()
    return data


def get_daily_spent(user_id):
    today = str(date.today())

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=? AND created_at=?",
        (user_id, today)
    )

    total = cursor.fetchone()[0] or 0
    conn.close()
    return total


def get_weekly_spent(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=?",
        (user_id,)
    )

    total = cursor.fetchone()[0] or 0
    conn.close()
    return total


def check_alert(user_id):
    daily_limit, weekly_limit = get_limits(user_id)

    daily = get_daily_spent(user_id)
    weekly = get_weekly_spent(user_id)

    if daily_limit and daily >= daily_limit:
        return "⚠️ Daily limit reached!"

    if weekly_limit and weekly >= weekly_limit:
        return "⚠️ Weekly limit reached!"

    return None

def get_salary(user_id):
    import sqlite3
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT amount FROM salary WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0