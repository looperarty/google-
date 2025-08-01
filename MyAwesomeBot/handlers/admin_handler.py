# handlers/admin_handler.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from html import escape

from config import ADMIN_ID, MDL_PER_CREDIT
from database import get_total_users, get_total_video_creations, get_total_free_generations, get_daily_payments, add_balance, get_pending_requests, delete_pending_request, get_user_sequential_id, get_total_subscribers

router = Router()

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Общая статистика", callback_data="show_stats_all")],
        [InlineKeyboardButton(text="📝 Ожидающие запросы", callback_data="show_pending_requests")],
    ])
    await message.answer("🔑 **Админ-панель**\n\nВыберите, что хотите посмотреть:", reply_markup=keyboard)


@router.callback_query(F.data == "show_stats_all")
async def show_all_stats_callback(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    total_users = await get_total_users()
    total_generations = await get_total_video_creations()
    free_generations = await get_total_free_generations()
    total_subscribers = await get_total_subscribers()
    total_payments = await get_daily_payments()
    
    stats_message = (
        "📊 **Общая статистика:**\n\n"
        f"👥 **Всего подписчиков:** {total_subscribers}\n"
        f"👥 **Всего пользователей:** {total_users}\n\n"
        f"🎬 **Количество генераций:** {total_generations}\n"
        f"   - Бесплатных: {free_generations}\n\n"
        f"💳 **Заработано за сегодня:**\n"
        f"   **{total_payments}** кредитов\n\n"
        "**Команды для работы:**\n"
        "/pending - посмотреть список ожидающих запросов\n"
        "/addcredits <id> <сумма> - начислить кредиты\n\n"
        "**Для отправки видео:**\n"
        "Отправь видео в бот с подписью: `/send <ID_пользователя>`"
    )
    
    await callback.message.answer(stats_message)
    await callback.answer()


@router.callback_query(F.data == "show_pending_requests")
async def show_pending_requests_callback(callback: CallbackQuery) -> None:
    if callback.from_user.id != ADMIN_ID:
        return

    requests = await get_pending_requests()
    
    if not requests:
        await callback.message.answer("Список ожидающих запросов пуст.")
        return

    requests_message = "📝 **Ожидающие запросы:**\n\n"
    for user_id, prompt, type in requests:
        sequential_id = await get_user_sequential_id(user_id)
        requests_message += f"**Порядковый номер:** <code>{sequential_id}</code>\n"
        requests_message += f"**ID пользователя:** <code>{user_id}</code>\n"
        requests_message += f"**Тип:** <code>{type}</code>\n"
        requests_message += f"**Промт:** <code>{escape(prompt)}</code>\n\n"
    
    await callback.message.answer(requests_message)
    await callback.answer()

@router.message(F.from_user.id == ADMIN_ID, F.video)
async def send_video_handler(message: Message) -> None:
    command_text = message.caption
    
    if command_text and command_text.startswith('/send'):
        try:
            user_id = int(command_text.split()[1])
            
            requests = await get_pending_requests()
            request_exists = any(req_user_id == user_id for req_user_id, _, _ in requests)
            
            if request_exists:
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