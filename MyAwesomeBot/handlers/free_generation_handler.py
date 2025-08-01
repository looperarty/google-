# handlers/free_generation_handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.common_handlers import create_back_keyboard, simulate_progress_bar
from handlers.menu_handler import create_main_menu_keyboard
from database import get_free_generations_used, use_free_generation
from config import PROMPTS_CHANNEL_LINK, ADMIN_ID

router = Router()

class FreeGenerationState(StatesGroup):
    """Состояние для процесса бесплатной генерации."""
    waiting_for_prompt = State()
    waiting_for_admin_response = State()

@router.message(F.text == "🎁 Бесплатная генерация")
async def free_generation_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    """Обрабатывает кнопку 'Бесплатная генерация'."""
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    free_uses = await get_free_generations_used(message.from_user.id)
    
    if free_uses > 0:
        await message.answer("Ты уже использовал свою бесплатную генерацию. Пригласи друга, чтобы получить бонусы.")
        return
    
    await state.set_state(FreeGenerationState.waiting_for_prompt)
    sent_message = await message.answer(
        "Напиши промт для бесплатного видео. Опиши, что ты хочешь увидеть:",
        reply_markup=await create_back_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)

@router.message(FreeGenerationState.waiting_for_prompt)
async def process_free_prompt(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает промт и отправляет его админу."""
    state_data = await state.get_data()
    bot_message_id = state_data.get('bot_message_id')
    
    await delete_message_if_exists(bot, message.chat.id, bot_message_id)
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    user_prompt = message.text
    user_id = message.from_user.id
    
    # Запускаем шкалу загрузки
    await simulate_progress_bar(message, bot)

    await use_free_generation(user_id)
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новый запрос на БЕСПЛАТНОЕ видео от пользователя `{user_id}`:\n\n**Промт:** `{user_prompt}`",
    )
    
    keyboard = await create_main_menu_keyboard()
    await message.answer(
        "Твой запрос принят! Мы создадим видео и отправим его тебе.",
        reply_markup=keyboard
    )
    await state.clear()