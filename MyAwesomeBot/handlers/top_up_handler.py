# handlers/top_up_handler.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_balance
from handlers.common_handlers import create_cancel_keyboard # <-- Добавили этот импорт

router = Router()

class TopUpState(StatesGroup):
    """Состояние для пополнения баланса."""
    waiting_for_amount = State()

@router.message(F.text == "Пополнить баланс")
async def start_top_up(message: Message, state: FSMContext):
    """Начинает процесс пополнения баланса."""
    await state.set_state(TopUpState.waiting_for_amount)
    await message.answer(
        "Введите сумму, на которую хотите пополнить баланс.",
        reply_markup=await create_cancel_keyboard() # <-- Изменили эту строку
    )

@router.message(TopUpState.waiting_for_amount)
async def process_top_up_amount(message: Message, state: FSMContext):
    """Обрабатывает введенную сумму."""
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
        
        await add_balance(message.from_user.id, amount)
        await message.answer(f"Баланс успешно пополнен на **{amount}** кредитов!")
        await state.clear()
        
    except (ValueError, TypeError):
        await message.answer("Пожалуйста, введите корректное число.")