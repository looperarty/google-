# handlers/video_handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_user_balance, deduct_balance_and_use_subscription
from handlers.menu_handler import create_main_menu_keyboard
from handlers.common_handlers import create_cancel_keyboard, delete_message_if_exists

router = Router()

VIDEO_COST = 10 # Стоимость одного видео в кредитах

class VideoCreationState(StatesGroup):
    """Состояние для процесса создания видео."""
    waiting_for_prompt = State()

@router.message(F.text == "🎬 Создать видео")
async def start_video_creation(message: Message, state: FSMContext, bot: Bot):
    """Начинает процесс создания видео."""
    balance = await get_user_balance(message.from_user.id)
    
    if balance < VIDEO_COST:
        await message.answer(f"У тебя недостаточно кредитов для создания видео. Стоимость: **{VIDEO_COST}** кредитов, твой баланс: **{balance}**.")
        return
        
    await state.set_state(VideoCreationState.waiting_for_prompt)
    sent_message = await message.answer(
        "Напиши промт для видео. Опиши, что ты хочешь увидеть:",
        reply_markup=await create_cancel_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)

@router.message(VideoCreationState.waiting_for_prompt)
async def process_video_prompt(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает промт и 'создаёт' видео."""
    state_data = await state.get_data()
    bot_message_id = state_data.get('bot_message_id')
    
    await delete_message_if_exists(bot, message.chat.id, bot_message_id)
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    try:
        user_prompt = message.text
        
        # Используем новую функцию, которая проверяет и списывает подписку
        success, email = await deduct_balance_and_use_subscription(message.from_user.id, VIDEO_COST)
        
        if success:
            await message.answer(f"Отлично! Начинаю создавать видео с использованием почты `{email}` по твоему промту: `{user_prompt}`. Это займет некоторое время.")
        else:
            await message.answer("Не удалось списать кредиты. Возможно, все подписки сейчас заняты. Попробуй снова через некоторое время.")
    finally:
        keyboard = await create_main_menu_keyboard()
        await message.answer(
            "Твоё видео готово! (Заглушка).",
            reply_markup=keyboard
        )
        await state.clear()