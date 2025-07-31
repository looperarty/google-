# handlers/top_up_handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_balance
from handlers.common_handlers import create_cancel_keyboard, delete_message_if_exists

router = Router()

class TopUpState(StatesGroup):
    """Состояние для пополнения баланса."""
    waiting_for_amount = State()

@router.message(F.text == "💳 Пополнить баланс")
async def start_top_up(message: Message, state: FSMContext, bot: Bot):
    """Начинает процесс пополнения баланса."""
    sent_message = await message.answer(
        "Введите сумму, на которую хотите пополнить баланс.",
        reply_markup=await create_cancel_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)
    await state.set_state(TopUpState.waiting_for_amount)

@router.message(TopUpState.waiting_for_amount)
async def process_top_up_amount(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает введенную сумму."""
    state_data = await state.get_data()
    bot_message_id = state_data.get('bot_message_id')
    
    await delete_message_if_exists(bot, message.chat.id, bot_message_id)
    await delete_message_if_exists(bot, message.chat.id, message.message_id)

    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
        
        await add_balance(message.from_user.id, amount)
        await message.answer(f"Баланс успешно пополнен на **{amount}** кредитов!")
        await state.clear()
        
    except (ValueError, TypeError):
        await message.answer("Пожалуйста, введите корректное число.")