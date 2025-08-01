# handlers/video_handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_user_balance, deduct_balance_and_use_subscription
from handlers.menu_handler import create_main_menu_keyboard
from handlers.common_handlers import create_back_keyboard, delete_message_if_exists, simulate_progress_bar
from config import ADMIN_ID

router = Router()

VIDEO_COST = 10

class VideoCreationState(StatesGroup):
    """Состояние для создания видео."""
    waiting_for_prompt = State()
    waiting_for_admin_response = State()

@router.message(F.text == "🎬 Создать видео")
async def start_video_creation(message: Message, state: FSMContext, bot: Bot):
    """Начинает процесс создания видео."""
    await delete_message_if_exists(bot, message.chat.id, message.message_id)

    # Проверяем, если это админ, пропускаем проверку баланса
    if message.from_user.id != ADMIN_ID:
        balance = await get_user_balance(message.from_user.id)
        if balance < VIDEO_COST:
            sent_message = await message.answer(f"У тебя недостаточно кредитов для создания видео. Стоимость: **{VIDEO_COST}** кредитов, твой баланс: **{balance}**.")
            await state.update_data(bot_message_id=sent_message.message_id)
            return
        
    await state.set_state(VideoCreationState.waiting_for_prompt)
    sent_message = await message.answer(
        "Напиши промт для видео. Опиши, что ты хочешь увидеть:",
        reply_markup=await create_back_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)

@router.message(VideoCreationState.waiting_for_prompt)
async def process_video_prompt(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает введенный промт и отправляет его админу."""
    state_data = await state.get_data()
    bot_message_id = state_data.get('bot_message_id')
    
    await delete_message_if_exists(bot, message.chat.id, bot_message_id)
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    user_prompt = message.text
    user_id = message.from_user.id

    await simulate_progress_bar(message, bot)
    
    # Отправляем промт админу
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новый запрос на видео от пользователя `{user_id}`:\n\n**Промт:** `{user_prompt}`",
    )
    
    # Сохраняем состояние для ответа админа
    await state.set_state(VideoCreationState.waiting_for_admin_response)
    
    keyboard = await create_main_menu_keyboard()
    await message.answer(
        "Твой запрос принят! Мы создадим видео и отправим его тебе. Это займет некоторое время.",
        reply_markup=keyboard
    )
    await state.clear()