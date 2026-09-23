import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "expense_tracker.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            amount REAL NOT NULL CHECK(amount > 0)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            amount REAL NOT NULL DEFAULT 25000
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO budget (id, amount)
        VALUES (1, 25000)
    """)

    conn.commit()
    conn.close()


def add_transaction(date, category, description, transaction_type, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions
        (date, category, description, type, amount)
        VALUES (?, ?, ?, ?, ?)
    """, (date, category, description, transaction_type, amount))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    return transaction_id


def get_transactions():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, date, category, description, type, amount
        FROM transactions
        ORDER BY date DESC, id DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_transaction(transaction_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )
    conn.commit()
    conn.close()


def get_budget():
    conn = get_connection()
    row = conn.execute(
        "SELECT amount FROM budget WHERE id = 1"
    ).fetchone()
    conn.close()
    return float(row["amount"]) if row else 25000.0


def set_budget(amount):
    conn = get_connection()
    conn.execute(
        "UPDATE budget SET amount = ? WHERE id = 1",
        (amount,)
    )
    conn.commit()
    conn.close()


initialize_database()
