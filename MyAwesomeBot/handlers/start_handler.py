# handlers/start_handler.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.menu_handler import create_main_menu_keyboard
from database import add_or_update_user
from config import ADMIN_ID

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    keyboard = await create_main_menu_keyboard()
    await add_or_update_user(message.from_user.id, message.from_user.username)
    await message.answer(
        f"Привет, **{message.from_user.full_name}**! Я твой бот для создания видео.\n\n"
        "Выбери, что будем делать:",
        reply_markup=keyboard
    )
    
    # Отправляем админ-панель только тебе
    if message.from_user.id == ADMIN_ID:
        admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Админ-панель", callback_data="show_admin_panel")]
        ])
        await message.answer("Добро пожаловать, админ!", reply_markup=admin_keyboard)