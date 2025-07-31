# handlers/start_handler.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from handlers.menu_handler import create_main_menu_keyboard
from database import add_or_update_user

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот хендлер будет вызываться при получении команды /start.
    """
    keyboard = await create_main_menu_keyboard()
    await add_or_update_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет, **{message.from_user.full_name}**! Я твой бот для создания видео.\n\n"
        "Выбери, что будем делать:",
        reply_markup=keyboard
    )