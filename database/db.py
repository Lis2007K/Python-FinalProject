"""
Database helper using sqlite3.
Contains initialization and basic CRUD operations used by the Streamlit frontend.
"""

import sqlite3
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from config import settings
from .models import User, Transaction
import hashlib


def get_connection():
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        ttype TEXT NOT NULL CHECK(ttype IN ('income','expense')),
        description TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    conn.commit()
    conn.close()


# ----------------- User functions -----------------
def _hash_password(password: str) -> str:
    salted = (password + settings.SECRET_SALT).encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def create_user(username: str, password: str) -> Tuple[bool, str]:
    """
    Returns (success, message)
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        pw_hash = _hash_password(password)
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, pw_hash, datetime.utcnow().isoformat())
        )
        conn.commit()
        return True, "User created"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[User]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, created_at FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return User.from_row(row)


def verify_user(username: str, password: str) -> Tuple[bool, Optional[User]]:
    user = get_user_by_username(username)
    if user is None:
        return False, None
    if user.password_hash == _hash_password(password):
        return True, user
    return False, None


# ----------------- Transaction functions -----------------
def add_transaction(user_id: int, date_iso: str, amount: float, category: str, ttype: str, description: str = None) -> Tuple[bool, str]:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (user_id, date, amount, category, ttype, description) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, date_iso, amount, category, ttype, description)
        )
        conn.commit()
        return True, "Saved"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def get_transactions_by_user(user_id: int, limit: int = 200) -> List[Transaction]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, date, amount, category, ttype, description FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [Transaction.from_row(tuple(r)) for r in rows]


def get_transaction_by_id(tx_id: int) -> Optional[Transaction]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, user_id, date, amount, category, ttype, description FROM transactions WHERE id = ?",
        (tx_id,)
    )
    row = cur.fetchone()
    conn.close()
    return Transaction.from_row(tuple(row)) if row else None


def get_balance(user_id: int) -> float:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(CASE WHEN ttype='income' THEN amount ELSE -amount END) as balance FROM transactions WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return float(row["balance"]) if row and row["balance"] is not None else 0.0


def get_monthly_summary(user_id: int) -> List[Dict]:
    """
    Returns monthly totals grouped by YYYY-MM (list of dicts with 'month','income','expense')
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT substr(date,1,7) as month,
           SUM(CASE WHEN ttype='income' THEN amount ELSE 0 END) as income,
           SUM(CASE WHEN ttype='expense' THEN amount ELSE 0 END) as expense
    FROM transactions
    WHERE user_id = ?
    GROUP BY month
    ORDER BY month ASC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    summary = []
    for r in rows:
        summary.append({"month": r["month"], "income": float(r["income"] or 0.0), "expense": float(r["expense"] or 0.0)})
    return summary


def update_transaction(tx_id: int, user_id: int, date_iso: str, amount: float, category: str, ttype: str, description: str = None) -> Tuple[bool, str]:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE transactions SET date = ?, amount = ?, category = ?, ttype = ?, description = ? WHERE id = ? AND user_id = ?",
            (date_iso, amount, category, ttype, description, tx_id, user_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            return False, "Transaction not found or not authorized"
        return True, "Updated"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()


def delete_transaction(tx_id: int, user_id: int) -> Tuple[bool, str]:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM transactions WHERE id = ? AND user_id = ?",
            (tx_id, user_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            return False, "Transaction not found or not authorized"
        return True, "Deleted"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()
