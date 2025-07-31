# handlers/free_generation_handler.py

from aiogram import Router, F
from aiogram.types import Message
from handlers.menu_handler import create_main_menu_keyboard
from database import get_free_generations_used, use_free_generation

router = Router()

@router.message(F.text == "🎁 Бесплатная генерация")
async def free_generation_handler(message: Message) -> None:
    """Обрабатывает кнопку 'Бесплатная генерация'."""
    free_uses = await get_free_generations_used(message.from_user.id)
    
    if free_uses > 0:
        await message.answer("Ты уже использовал свою бесплатную генерацию.")
        return
        
    await use_free_generation(message.from_user.id)
    
    await message.answer("Отлично! Начинаю бесплатную генерацию видео. Это займет некоторое время.")
    
    keyboard = await create_main_menu_keyboard()
    await message.answer(
        "Твоё бесплатное видео готово! (Заглушка).",
        reply_markup=keyboard
    )