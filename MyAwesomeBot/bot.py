import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers.start_handler import router as start_router
from handlers.menu_handler import router as menu_router
from handlers.top_up_handler import router as top_up_router
from handlers.video_handler import router as video_router
from handlers.common_handlers import router as common_router
from handlers.admin_handler import router as admin_router
from database import init_db

# Включаем логирование, чтобы видеть ошибки и отладочные сообщения
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

async def main():
    """
    Основная функция для запуска бота.
    """
    # Инициализируем базу данных
    await init_db()
    
    # Регистрируем роутеры с хендлерами
    dp.include_router(common_router)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(top_up_router) # <-- Исправлено
    dp.include_router(video_router)
    dp.include_router(admin_router)
    
    # Удаляем все команды и настройки, которые могли остаться от предыдущих запусков
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем основной цикл бота
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    # Запускаем асинхронную функцию main()
    asyncio.run(main())