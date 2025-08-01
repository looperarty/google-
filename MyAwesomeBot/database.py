# database.py

import sqlite3
from datetime import datetime
import uuid

DB_NAME = "database.db"
MAX_DAILY_USES = 50

async def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            sequential_id INTEGER UNIQUE,
            username TEXT,
            balance INTEGER DEFAULT 0,
            free_generations_used INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_creations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            daily_limit INTEGER DEFAULT 50,
            daily_usage INTEGER DEFAULT 0,
            last_used DATETIME
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_requests (
            user_id INTEGER PRIMARY KEY,
            prompt TEXT,
            type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

async def get_user_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def add_or_update_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user_exists = cursor.fetchone()
    if not user_exists:
        cursor.execute("SELECT MAX(sequential_id) FROM users")
        max_id = cursor.fetchone()[0]
        new_id = (max_id or 0) + 1
        
        referral_code = str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO users (user_id, sequential_id, username, free_generations_used, referral_code) VALUES (?, ?, ?, ?, ?)", (user_id, new_id, username, 0, referral_code))
    conn.commit()
    conn.close()

async def get_total_users() -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def get_user_sequential_id(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sequential_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

async def add_balance(user_id: int, amount: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, user_id)
    )
    cursor.execute("INSERT INTO payments (user_id, amount) VALUES (?, ?)", (user_id, amount))
    conn.commit()
    conn.close()
    
async def deduct_balance(user_id: int, amount: int) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    current_balance = cursor.fetchone()[0]
    if current_balance >= amount:
        cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id)
        )
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

async def deduct_balance_and_use_subscription(user_id: int, amount: int) -> tuple[bool, str | None]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if not await deduct_balance(user_id, amount):
        conn.close()
        return False, None
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("UPDATE subscriptions SET daily_usage = 0 WHERE last_used < ?", (today_start,))

    cursor.execute(
        "SELECT email FROM subscriptions WHERE daily_usage < daily_limit ORDER BY daily_usage ASC LIMIT 1"
    )
    subscription_email = cursor.fetchone()

    if subscription_email:
        subscription_email = subscription_email[0]
        cursor.execute(
            "UPDATE subscriptions SET daily_usage = daily_usage + 1, last_used = ? WHERE email = ?",
            (datetime.now(), subscription_email)
        )
        cursor.execute("INSERT INTO video_creations (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return True, subscription_email
    else:
        cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        conn.commit()
        conn.close()
        return False, None

async def get_daily_video_creations() -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("SELECT COUNT(*) FROM video_creations WHERE timestamp >= ?", (today_start,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def get_daily_payments() -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("SELECT SUM(amount) FROM payments WHERE timestamp >= ?", (today_start,))
    total_payments = cursor.fetchone()[0]
    conn.close()
    return total_payments if total_payments else 0

async def get_free_generations_used(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT free_generations_used FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def use_free_generation(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET free_generations_used = free_generations_used + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

async def get_referral_code(user_id: int) -> str | None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT referral_code FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
    
async def add_pending_request(user_id: int, prompt: str, type: str):
    """Добавляет запрос в список ожидающих."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO pending_requests (user_id, prompt, type) VALUES (?, ?, ?)",
        (user_id, prompt, type)
    )
    conn.commit()
    conn.close()

async def get_pending_requests() -> list:
    """Возвращает все ожидающие запросы."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, prompt, type FROM pending_requests ORDER BY timestamp ASC")
    requests = cursor.fetchall()
    conn.close()
    return requests

async def delete_pending_request(user_id: int):
    """Удаляет запрос из списка."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pending_requests WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()