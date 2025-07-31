# database.py

import sqlite3
from datetime import datetime

# Путь к файлу базы данных
DB_NAME = "database.db"

async def init_db():
    """Инициализирует базу данных и создаёт таблицы."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создаём таблицу 'users', если её ещё нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0
        )
    """)

    # Создаём таблицу для учёта созданных видео
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_creations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Создаём таблицу для учёта пополнений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

async def get_user_balance(user_id: int) -> int:
    """Возвращает баланс пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

async def add_or_update_user(user_id: int, username: str):
    """Добавляет нового пользователя или обновляет существующего."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    user_exists = cursor.fetchone()
    if not user_exists:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

async def add_balance(user_id: int, amount: int):
    """Увеличивает баланс пользователя и записывает платёж."""
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
    """Списывает кредиты и записывает создание видео."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    current_balance = cursor.fetchone()[0]
    if current_balance >= amount:
        cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id)
        )
        cursor.execute("INSERT INTO video_creations (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

async def get_total_users() -> int:
    """Возвращает общее количество пользователей."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def get_daily_video_creations() -> int:
    """Возвращает количество созданных видео за текущий день."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("SELECT COUNT(*) FROM video_creations WHERE timestamp >= ?", (today_start,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def get_daily_payments() -> int:
    """Возвращает общую сумму пополнений за текущий день."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cursor.execute("SELECT SUM(amount) FROM payments WHERE timestamp >= ?", (today_start,))
    total_payments = cursor.fetchone()[0]
    conn.close()
    return total_payments if total_payments else 0