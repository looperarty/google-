# handlers/menu_handler.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from database import get_user_balance
from config import PROMPTS_CHANNEL_LINK, SUPPORT_LINK

router = Router()

async def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с основными кнопками."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Создать видео")],
            [KeyboardButton(text="🎁 Бесплатная генерация")],
            [KeyboardButton(text="💰 Мой баланс"), KeyboardButton(text="💳 Пополнить баланс")],
            [KeyboardButton(text="📚 Канал с промтами"), KeyboardButton(text="👋 Пригласить друга")],
            [KeyboardButton(text="📞 Служба поддержки")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

@router.message(F.text == "💰 Мой баланс")
async def handle_my_balance(message: Message):
    user_balance = await get_user_balance(message.from_user.id)
    await message.answer(f"Твой текущий баланс: **{user_balance}** кредитов.")

@router.message(F.text == "📚 Канал с промтами")
async def handle_prompts_channel(message: Message):
    await message.answer(f"Подписывайся на наш канал, чтобы не пропустить новые промты: <a href='{PROMPTS_CHANNEL_LINK}'>Канал с промтами</a>")

@router.message(F.text == "📞 Служба поддержки")
async def handle_support(message: Message):
    await message.answer(f"Если у тебя есть вопросы, напиши в нашу службу поддержки: <a href='{SUPPORT_LINK}'>Служба поддержки</a>.")

@router.message(F.text == "👋 Пригласить друга")
async def handle_invite_friend(message: Message):
    await message.answer(
        f"Пригласи друга в наш канал, чтобы получить бонусы: <a href='{PROMPTS_CHANNEL_LINK}'>Пригласить друга</a>"
    )