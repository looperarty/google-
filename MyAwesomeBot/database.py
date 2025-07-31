# database.py

import sqlite3
from datetime import datetime

# Путь к файлу базы данных
DB_NAME = "database.db"

# Максимальное количество использований одной подписки в день
MAX_DAILY_USES = 50

async def init_db():
    """Инициализирует базу данных и создаёт таблицы."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0
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
    """Списывает кредиты."""
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
    """Списывает кредиты, находит подписку и записывает использование."""
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

# Новые функции для управления подписками

async def add_subscription(email: str) -> bool:
    """Добавляет новую подписку."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subscriptions (email, daily_limit, daily_usage) VALUES (?, ?, ?)", 
                       (email, MAX_DAILY_USES, 0))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Такая почта уже существует
        return False
    finally:
        conn.close()

async def get_all_subscriptions() -> list:
    """Возвращает список всех подписок."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email, daily_usage, daily_limit FROM subscriptions")
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions

async def reset_all_subscriptions() -> bool:
    """Сбрасывает счётчик использования всех подписок."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET daily_usage = 0")
    conn.commit()
    conn.close()
    return True