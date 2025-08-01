# handlers/admin_handler.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_ID
from database import get_total_users, get_daily_video_creations, get_daily_payments

router = Router()

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    await send_admin_panel_stats(message)

@router.callback_query(F.data == "show_admin_panel")
async def show_admin_panel_callback(callback: CallbackQuery) -> None:
    if callback.from_user.id != ADMIN_ID:
        return
    
    await send_admin_panel_stats(callback.message)
    await callback.answer()

async def send_admin_panel_stats(message: Message):
    """Отправляет сообщение с админ-статистикой."""
    total_users = await get_total_users()
    daily_creations = await get_daily_video_creations()
    daily_payments = await get_daily_payments()
    
    stats_message = (
        "📈 **Админ-панель**\n\n"
        f"👥 **Статистика клиентов:**\n"
        f"   Всего пользователей: **{total_users}**\n"
        f"   Посетителей бота: **{total_users}**\n\n"
        f"🎬 **Количество генераций в день:**\n"
        f"   Всего: **{daily_creations}**\n"
        f"   Бесплатных: (Эта статистика пока недоступна)\n\n"
        f"💳 **Сколько заработано за сегодня:**\n"
        f"   **{daily_payments}** кредитов"
    )
    
    await message.answer(stats_message)