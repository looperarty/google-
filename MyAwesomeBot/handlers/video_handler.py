# handlers/video_handler.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_user_balance, deduct_balance
from handlers.menu_handler import create_main_menu_keyboard

router = Router()

VIDEO_COST = 10 # Стоимость одного видео в кредитах

class VideoCreationState(StatesGroup):
    """Состояние для процесса создания видео."""
    waiting_for_prompt = State()

@router.message(F.text == "Создать видео")
async def start_video_creation(message: Message, state: FSMContext):
    """Начинает процесс создания видео."""
    balance = await get_user_balance(message.from_user.id)
    
    if balance < VIDEO_COST:
        await message.answer(f"У тебя недостаточно кредитов для создания видео. Стоимость: **{VIDEO_COST}** кредитов, твой баланс: **{balance}**.")
        return
        
    await state.set_state(VideoCreationState.waiting_for_prompt)
    await message.answer(
        "Напиши промт для видео. Опиши, что ты хочешь увидеть:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(VideoCreationState.waiting_for_prompt)
async def process_video_prompt(message: Message, state: FSMContext):
    """Обрабатывает промт и 'создаёт' видео."""
    user_prompt = message.text
    
    # Списываем кредиты
    success = await deduct_balance(message.from_user.id, VIDEO_COST)
    
    if success:
        # Здесь должна быть логика вызова API для создания видео (например, Google Veo)
        # Пока что это просто заглушка
        await message.answer(f"Отлично! Начинаю создавать видео по твоему промту: `{user_prompt}`. Это займет некоторое время.")
        
        # После завершения процесса возвращаем основную клавиатуру
        keyboard = await create_main_menu_keyboard()
        await message.answer(
            "Твоё видео готово! (Заглушка).",
            reply_markup=keyboard
        )
    else:
        # Если списание не удалось (например, пользователь пополнил баланс, но использовал его в другом месте)
        await message.answer("Не удалось списать кредиты. Пожалуйста, попробуй снова или пополни баланс.")
    
    await state.clear()