# handlers/admin_handler.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMIN_ID
from database import get_total_users, get_daily_video_creations, get_daily_payments # <-- Обновили импорты

router = Router()

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    """Обрабатывает команду /admin и показывает статистику."""
    # Проверяем, является ли пользователь администратором
    if message.from_user.id != ADMIN_ID:
        return
    
    total_users = await get_total_users()
    daily_creations = await get_daily_video_creations()
    daily_payments = await get_daily_payments()
    
    stats_message = (
        "📈 **Админ-панель**\n\n"
        f"👥 Всего пользователей: **{total_users}**\n"
        f"🎬 Просмотров за сегодня: **{daily_creations}**\n"
        f"💳 Поступлений за сегодня: **{daily_payments}** кредитов"
    )
    
    await message.answer(stats_message)