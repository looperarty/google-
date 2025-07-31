# handlers/top_up_handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_balance
from handlers.common_handlers import create_back_keyboard, delete_message_if_exists
from handlers.menu_handler import create_main_menu_keyboard

router = Router()

class TopUpState(StatesGroup):
    """Состояние для пополнения баланса."""
    waiting_for_amount = State()

@router.message(F.text == "💳 Пополнить баланс")
async def start_top_up(message: Message, state: FSMContext, bot: Bot):
    """Начинает процесс пополнения баланса."""
    # Сохраняем ID предыдущего сообщения пользователя, чтобы потом его удалить
    await state.update_data(user_message_id=message.message_id)
    
    sent_message = await message.answer(
        "Введите сумму, на которую хотите пополнить баланс.",
        reply_markup=await create_back_keyboard()
    )
    # Сохраняем ID сообщения бота
    await state.update_data(bot_message_id=sent_message.message_id)
    await state.set_state(TopUpState.waiting_for_amount)

@router.message(TopUpState.waiting_for_amount)
async def process_top_up_amount(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает введенную сумму."""
    state_data = await state.get_data()
    user_message_id = state_data.get('user_message_id')
    bot_message_id = state_data.get('bot_message_id')
    
    # Удаляем предыдущие сообщения, чтобы не засорять чат
    await delete_message_if_exists(bot, message.chat.id, user_message_id)
    await delete_message_if_exists(bot, message.chat.id, bot_message_id)
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
        
        await add_balance(message.from_user.id, amount)
        keyboard = await create_main_menu_keyboard()
        await message.answer(f"Баланс успешно пополнен на **{amount}** кредитов!", reply_markup=keyboard)
        await state.clear()
        
    except (ValueError, TypeError):
        keyboard = await create_back_keyboard()
        sent_message = await message.answer("Пожалуйста, введите корректное число.", reply_markup=keyboard)
        await state.update_data(bot_message_id=sent_message.message_id)