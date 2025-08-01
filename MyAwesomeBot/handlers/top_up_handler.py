# handlers/top_up_handler.py

from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_balance
from handlers.common_handlers import create_back_keyboard, delete_message_if_exists
from handlers.menu_handler import create_main_menu_keyboard
from config import ADMIN_ID

router = Router()

class TopUpState(StatesGroup):
    """Состояния для пополнения баланса."""
    waiting_for_payment_method = State()
    waiting_for_confirmation = State()
    waiting_for_screenshot = State()

async def create_payment_methods_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с вариантами оплаты."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Номер карты")],
            [KeyboardButton(text="MIA (Молдова)")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

async def create_payment_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой 'Я оплатил'."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Я оплатил")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

@router.message(F.text == "💳 Пополнить баланс")
async def start_top_up(message: Message, state: FSMContext, bot: Bot):
    """Начинает процесс пополнения баланса, предлагая выбор способа."""
    sent_message = await message.answer(
        "Выберите способ оплаты:",
        reply_markup=await create_payment_methods_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)
    await state.set_state(TopUpState.waiting_for_payment_method)
    
@router.message(TopUpState.waiting_for_payment_method, F.text == "Номер карты")
async def process_card_payment(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает выбор 'Номер карты'."""
    await delete_message_if_exists(bot, message.chat.id, (await state.get_data()).get('bot_message_id'))
    await delete_message_if_exists(bot, message.chat.id, message.message_id)

    sent_message = await message.answer(
        "Чтобы пополнить баланс, переведите деньги на номер карты:\n\n**1234 5678 9012 3456**\n\nКогда оплатите, нажмите кнопку ниже:",
        reply_markup=await create_payment_confirmation_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)
    await state.set_state(TopUpState.waiting_for_confirmation)
    
@router.message(TopUpState.waiting_for_payment_method, F.text == "MIA (Молдова)")
async def process_mia_payment(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает выбор 'MIA (Молдова)'."""
    await delete_message_if_exists(bot, message.chat.id, (await state.get_data()).get('bot_message_id'))
    await delete_message_if_exists(bot, message.chat.id, message.message_id)

    sent_message = await message.answer(
        "Чтобы пополнить баланс через MIA, переведите деньги по номеру:\n\n**+373 69 123 456**\n\nКогда оплатите, нажмите кнопку ниже:",
        reply_markup=await create_payment_confirmation_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)
    await state.set_state(TopUpState.waiting_for_confirmation)

@router.message(TopUpState.waiting_for_confirmation, F.text == "✅ Я оплатил")
async def request_screenshot(message: Message, state: FSMContext, bot: Bot):
    """Просит пользователя отправить скриншот после оплаты."""
    await delete_message_if_exists(bot, message.chat.id, (await state.get_data()).get('bot_message_id'))
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    sent_message = await message.answer(
        "Спасибо! Теперь пришлите скриншот или другое подтверждение оплаты.",
        reply_markup=await create_back_keyboard()
    )
    await state.update_data(bot_message_id=sent_message.message_id)
    await state.set_state(TopUpState.waiting_for_screenshot)

@router.message(TopUpState.waiting_for_screenshot)
async def process_top_up_amount(message: Message, state: FSMContext, bot: Bot):
    """Обрабатывает скриншот или другое подтверждение оплаты."""
    await delete_message_if_exists(bot, message.chat.id, (await state.get_data()).get('bot_message_id'))
    await delete_message_if_exists(bot, message.chat.id, message.message_id)
    
    # Отправляем подтверждение оплаты админу
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новое подтверждение оплаты от пользователя `{message.from_user.id}`:\n\n"
             "Пожалуйста, проверьте и начислите кредиты командой: `/addcredits {ID_пользователя} {сумма}`"
    )
    # Пересылаем сообщение пользователя админу
    await bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    
    await message.answer("Спасибо! Мы проверим вашу оплату в течение 2-3 минут и начислим кредиты.")
    
    await state.clear()
    keyboard = await create_main_menu_keyboard()
    await message.answer("Вы вернулись в главное меню.", reply_markup=keyboard)