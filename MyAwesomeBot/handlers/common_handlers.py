# handlers/common_handlers.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from handlers.menu_handler import create_main_menu_keyboard

router = Router()

async def create_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой 'Отмена'."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

@router.message(F.text == "Отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """Обрабатывает нажатие на кнопку 'Отмена'."""
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    keyboard = await create_main_menu_keyboard()
    await message.answer(
        "Действие отменено. Вы вернулись в главное меню.",
        reply_markup=keyboard
    )