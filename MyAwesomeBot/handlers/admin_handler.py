# handlers/admin_handler.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from html import escape

from config import ADMIN_ID, MDL_PER_CREDIT
from database import get_total_users, get_daily_video_creations, get_daily_payments, add_balance, get_pending_requests, delete_pending_request, get_user_sequential_id

router = Router()

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    await send_admin_panel_stats(message)

@router.callback_query(F.data == "show_admin_panel")
async def show_admin_panel_callback(callback: CallbackQuery) -> None:
    if callback.from_user.id != ADMIN_ID:
        return
    
    await send_admin_panel_stats(callback.message)
    await callback.answer()

async def send_admin_panel_stats(message: Message):
    total_users = await get_total_users()
    daily_creations = await get_daily_video_creations()
    daily_payments = await get_daily_payments()
    
    daily_earnings_mdl = daily_payments * MDL_PER_CREDIT
    
    stats_message = (
        "📈 **Админ-панель**\n\n"
        f"👥 **Статистика клиентов:**\n"
        f"   Всего пользователей: **{total_users}**\n"
        f"   Посетителей бота: **{total_users}**\n\n"
        f"🎬 **Количество генераций в день:**\n"
        f"   Всего: **{daily_creations}**\n"
        f"   Бесплатных: (Эта статистика пока недоступна)\n\n"
        f"💳 **Сколько заработано за сегодня:**\n"
        f"   **{daily_payments}** кредитов (приблизительно **{daily_earnings_mdl}** леев)"
    )
    
    await message.answer(stats_message)

@router.message(Command("pending"))
async def show_pending_requests_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    requests = await get_pending_requests()
    
    if not requests:
        await message.answer("Список ожидающих запросов пуст.")
        return

    requests_message = "📝 **Ожидающие запросы:**\n\n"
    for user_id, prompt, type in requests:
        sequential_id = await get_user_sequential_id(user_id)
        requests_message += f"**Порядковый номер:** <code>{sequential_id}</code>\n"
        requests_message += f"**ID пользователя:** <code>{user_id}</code>\n"
        requests_message += f"**Тип:** <code>{type}</code>\n"
        requests_message += f"**Промт:** <code>{escape(prompt)}</code>\n\n"
    
    await message.answer(requests_message)

@router.message(F.from_user.id == ADMIN_ID, F.video)
async def send_video_handler(message: Message) -> None:
    command_text = message.caption
    
    if command_text and command_text.startswith('/send'):
        try:
            user_id = int(command_text.split()[1])
            pending_requests = await get_pending_requests()
            
            if user_id in [req_user_id for req_user_id, _, _ in pending_requests]:
                await message.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                await message.answer(f"Видео успешно отправлено пользователю <code>{user_id}</code>.")
                await delete_pending_request(user_id)
            else:
                await message.answer(f"Запрос от пользователя <code>{user_id}</code> не найден.")

        except (ValueError, IndexError):
            await message.answer("Ошибка в команде. Используйте формат: `/send ID_пользователя`")
        except Exception as e:
            await message.answer(f"Не удалось отправить видео. Ошибка: {e}")

@router.message(Command("addcredits"))
async def add_credits_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        
        await add_balance(user_id, amount)
        await message.answer(f"Начислено **{amount}** кредитов пользователю <code>{user_id}</code>.")
    except (ValueError, IndexError):
        await message.answer("Ошибка в команде. Используйте формат: `/addcredits ID_пользователя сумма`")