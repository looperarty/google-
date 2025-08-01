# database.py

import sqlite3
from datetime import datetime, timedelta
import uuid

DB_NAME = "database.db"

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
            type TEXT,
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

async def get_total_video_creations(time_frame: str = "all") -> int:
    """Возвращает общее количество созданных видео за определенный период."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if time_frame == "today":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE timestamp >= ?", (start_date,))
    elif time_frame == "yesterday":
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE timestamp >= ? AND timestamp < ?", (yesterday, today))
    elif time_frame == "week":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE timestamp >= ?", (start_date,))
    elif time_frame == "month":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE timestamp >= ?", (start_date,))
    else:
        cursor.execute("SELECT COUNT(*) FROM video_creations")
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def get_total_free_generations(time_frame: str = "all") -> int:
    """Возвращает количество бесплатных генераций за определенный период."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if time_frame == "today":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE type = 'free' AND timestamp >= ?", (start_date,))
    elif time_frame == "yesterday":
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE type = 'free' AND timestamp >= ? AND timestamp < ?", (yesterday, today))
    elif time_frame == "week":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE type = 'free' AND timestamp >= ?", (start_date,))
    elif time_frame == "month":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE type = 'free' AND timestamp >= ?", (start_date,))
    else:
        cursor.execute("SELECT COUNT(*) FROM video_creations WHERE type = 'free'")
    
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

async def use_free_generation(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET free_generations_used = free_generations_used + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

async def get_free_generations_used(user_id: int) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT free_generations_used FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

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

async def get_total_subscribers() -> int:
    """Возвращает общее количество пользователей, которые использовали бесплатную генерацию (прошли проверку подписки)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE free_generations_used > 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count