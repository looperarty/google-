# handlers/common_handlers.py

import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from handlers.menu_handler import create_main_menu_keyboard

router = Router()

async def create_back_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой '⬅️ Назад'."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def delete_message_if_exists(bot: Bot, chat_id: int, message_id: int | None):
    """Удаляет сообщение, если его ID существует."""
    if message_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass

async def simulate_progress_bar(message: Message, bot: Bot):
    """
    Симулирует шкалу загрузки, редактируя сообщение.
    """
    progress_message = await bot.send_message(
        chat_id=message.chat.id,
        text="🎬 Начинаю генерацию видео..."
    )
    
    stages = ["", "▓░░░", "▓▓░░", "▓▓▓░", "▓▓▓▓"]
    
    for stage in stages:
        await bot.edit_message_text(
            text=f"🎬 Генерация: {stage}",
            chat_id=message.chat.id,
            message_id=progress_message.message_id
        )
        await asyncio.sleep(1) # Ждём 1 секунду

    await bot.edit_message_text(
        text="🎬 Генерация завершена!",
        chat_id=message.chat.id,
        message_id=progress_message.message_id
    )

@router.message(F.text == "⬅️ Назад")
async def back_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    """Обрабатывает нажатие на кнопку '⬅️ Назад'."""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    state_data = await state.get_data()
    await delete_message_if_exists(bot, message.chat.id, state_data.get('bot_message_id'))
    
    await state.clear()
    keyboard = await create_main_menu_keyboard()
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=keyboard
    )