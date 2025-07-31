# handlers/common_handlers.py

from aiogram import Router, F, Bot
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

async def delete_message_if_exists(bot: Bot, chat_id: int, message_id: int | None):
    """Удаляет сообщение, если его ID существует."""
    if message_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            # Игнорируем ошибки, если сообщение уже удалено
            pass

@router.message(F.text == "Отмена")
async def cancel_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    """Обрабатывает нажатие на кнопку 'Отмена'."""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    state_data = await state.get_data()
    await delete_message_if_exists(bot, message.chat.id, state_data.get('bot_message_id'))
    
    await state.clear()
    keyboard = await create_main_menu_keyboard()
    await message.answer(
        "Действие отменено. Вы вернулись в главное меню.",
        reply_markup=keyboard
    )