# handlers/referral_handler.py

from aiogram import Router, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER

from database import use_free_generation
from config import ADMIN_ID

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER), F.chat.id == -1002714712618)
async def referral_handler(event: ChatMemberUpdated):
    """Обрабатывает новых участников, пришедших по реферальной ссылке."""
    if event.invite_link and event.invite_link.invite_link.startswith(f"https://t.me/Modlovaveo3bot?start="):
        referral_code = event.invite_link.invite_link.split("?start=")[1]
        
        # Заглушка:
        await use_free_generation(event.from_user.id)
        
        # Отправляем сообщение администратору
        await event.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новый пользователь {event.new_chat_member.user.full_name} присоединился по реферальной ссылке с кодом {referral_code}."
        )