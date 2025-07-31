import sqlite3

# Путь к файлу базы данных
DB_NAME = "database.db"

async def init_db():
    """Инициализирует базу данных и создаёт таблицу пользователей."""
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

    conn.commit()
    conn.close()

async def get_user_balance(user_id: int) -> int:
    """Возвращает баланс пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()
    
    # Если пользователь не найден, возвращаем 0
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
    """Увеличивает баланс пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (amount, user_id)
    )

    conn.commit()
    conn.close()