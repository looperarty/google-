# handlers/free_generation_handler.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.common_handlers import create_back_keyboard
from handlers.menu_handler import create_main_menu_keyboard
from database import get_free_generations_used, use_free_generation, get_referral_code
from config import PROMPTS_CHANNEL_LINK

router = Router()

class FreeGenerationState(StatesGroup):
    """Состояние для процесса бесплатной генерации."""
    waiting_for_referral = State()

@router.message(F.text == "🎁 Бесплатная генерация")
async def free_generation_handler(message: Message, state: FSMContext) -> None:
    """Обрабатывает кнопку 'Бесплатная генерация'."""
    free_uses = await get_free_generations_used(message.from_user.id)
    
    if free_uses > 0:
        await message.answer("Ты уже использовал свою бесплатную генерацию.")
        return
        
    referral_code = await get_referral_code(message.from_user.id)
    
    await state.set_state(FreeGenerationState.waiting_for_referral)
    
    await message.answer(
        f"Чтобы получить бесплатную генерацию, пригласи друга в канал.\n\n"
        f"Твоя реферальная ссылка: `{PROMPTS_CHANNEL_LINK}?start={referral_code}`\n\n"
        "Как только твой друг присоединится, ты получишь генерацию."
    )

# Обработчик, который будет ждать, пока кто-то присоединится по ссылке
@router.message(FreeGenerationState.waiting_for_referral)
async def waiting_for_referral_handler(message: Message, state: FSMContext):
    await message.answer(
        "Я всё ещё жду, когда твой друг присоединится. Если ты хочешь вернуться, нажми '⬅️ Назад'.",
        reply_markup=await create_back_keyboard()
    )