# handlers/referral_handler.py

from aiogram import Router, F
from aiogram.types import ChatMemberUpdated, Message
from aiogram.filters import JOIN_TRANSITION

from database import use_free_generation
from config import ADMIN_ID

router = Router()

@router.chat_member(JOIN_TRANSITION, F.chat.id == ID_ТВОЕГО_КАНАЛА)
async def referral_handler(event: ChatMemberUpdated):
    """Обрабатывает новых участников, пришедших по реферальной ссылке."""
    if event.invite_link and event.invite_link.invite_link.startswith(f"https://t.me/твой_бот?start="):
        referral_code = event.invite_link.invite_link.split("?start=")[1]
        
        # Здесь должна быть логика, которая находит пользователя по реферальному коду
        # и начисляет ему бесплатную генерацию
        
        # Заглушка:
        await use_free_generation(event.from_user.id) # <-- Засчитываем реферал
        
        # Отправляем сообщение администратору
        await event.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новый пользователь {event.new_chat_member.user.full_name} присоединился по реферальной ссылке с кодом {referral_code}."
        )