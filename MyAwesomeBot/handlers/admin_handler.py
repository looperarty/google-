# handlers/admin_handler.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMIN_ID
from database import get_total_users, get_daily_video_creations, get_daily_payments, add_subscription, get_all_subscriptions, reset_all_subscriptions

router = Router()

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    """Обрабатывает команду /admin и показывает статистику."""
    if message.from_user.id != ADMIN_ID:
        return
    
    total_users = await get_total_users()
    daily_creations = await get_daily_video_creations()
    daily_payments = await get_daily_payments()
    
    stats_message = (
        "📈 **Админ-панель**\n\n"
        f"👥 Всего пользователей: **{total_users}**\n"
        f"🎬 Просмотров за сегодня: **{daily_creations}**\n"
        f"💳 Поступлений за сегодня: **{daily_payments}** кредитов\n\n"
        "**Команды для управления подписками:**\n"
        "/addsub <email>\n"
        "/listsubs\n"
        "/resetsubs"
    )
    
    await message.answer(stats_message)

@router.message(Command("addsub"))
async def add_subscription_handler(message: Message) -> None:
    """Добавляет новую подписку."""
    if message.from_user.id != ADMIN_ID:
        return
    
    email = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if not email:
        await message.answer("Пожалуйста, укажите почту: /addsub <email>")
        return
    
    success = await add_subscription(email)
    
    if success:
        await message.answer(f"Почта `{email}` успешно добавлена в пул подписок.")
    else:
        await message.answer(f"Ошибка: Почта `{email}` уже существует в базе данных.")

@router.message(Command("listsubs"))
async def list_subscriptions_handler(message: Message) -> None:
    """Показывает список подписок и их статус."""
    if message.from_user.id != ADMIN_ID:
        return
    
    subscriptions = await get_all_subscriptions()
    
    if not subscriptions:
        await message.answer("Пул подписок пуст. Добавьте почты с помощью /addsub.")
        return
        
    stats_message = "📧 **Пул подписок:**\n\n"
    for email, usage, limit in subscriptions:
        stats_message += f"`{email}`: {usage} из {limit} использований\n"
        
    await message.answer(stats_message)

@router.message(Command("resetsubs"))
async def reset_subscriptions_handler(message: Message) -> None:
    """Сбрасывает счётчики использования всех подписок."""
    if message.from_user.id != ADMIN_ID:
        return
    
    await reset_all_subscriptions()
    await message.answer("Счётчики использования всех подписок сброшены.")