import sqlite3

DB_NAME = "expense.db"


def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            telegram_id TEXT UNIQUE,
            daily_limit INTEGER DEFAULT 500,
            savings INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            day TEXT,
            amount INTEGER,
            note TEXT
        )
    """)

    con.commit()
    con.close()
