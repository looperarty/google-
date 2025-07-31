# handlers/menu_handler.py

from aiogram import Router, F
from aiogram.types import Message
from database import get_user_balance # <-- Добавили этот импорт

router = Router()

@router.message(F.text == "Создать видео")
async def handle_create_video(message: Message):
    """Обрабатывает нажатие на кнопку 'Создать видео'."""
    await message.answer("Окей, присылай промт для видео, и я начну работу.")

@router.message(F.text == "Мой баланс")
async def handle_my_balance(message: Message):
    """Обрабатывает нажатие на кнопку 'Мой баланс'."""
    user_balance = await get_user_balance(message.from_user.id) # <-- Изменили эту строку
    await message.answer(f"Твой текущий баланс: **{user_balance}** кредитов.") # <-- Изменили эту строку

@router.message(F.text == "Пополнить баланс")
async def handle_top_up_balance(message: Message):
    """Обрабатывает нажатие на кнопку 'Пополнить баланс'."""
    # TODO: Здесь будет ссылка на платёжную систему или инструкция
    await message.answer("Для пополнения баланса перейди по этой ссылке: [Ссылка для оплаты].")

@router.message(F.text == "Канал с промтами")
async def handle_prompts_channel(message: Message):
    """Обрабатывает нажатие на кнопку 'Канал с промтами'."""
    # TODO: Здесь будет ссылка на твой канал с промтами
    await message.answer("Подписывайся на наш канал, чтобы не пропустить новые промты: [Ссылка на канал].")

@router.message(F.text == "Служба поддержки")
async def handle_support(message: Message):
    """Обрабатывает нажатие на кнопку 'Служба поддержки'."""
    # TODO: Здесь будет ссылка на аккаунт поддержки или чат
    await message.answer("Если у тебя есть вопросы, напиши в нашу службу поддержки: [Ссылка на саппорт].")