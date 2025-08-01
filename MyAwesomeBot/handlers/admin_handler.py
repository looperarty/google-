# handlers/admin_handler.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMIN_ID
from database import get_total_users, get_daily_video_creations, get_daily_payments, add_subscription, get_all_subscriptions, reset_all_subscriptions, add_balance, get_pending_requests, delete_pending_request

router = Router()

@router.message(Command("admin"))
async def admin_panel_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    total_users = await get_total_users()
    daily_creations = await get_daily_video_creations()
    daily_payments = await get_daily_payments()
    
    stats_message = (
        "📈 **Админ-панель**\n\n"
        f"👥 Всего пользователей: **{total_users}**\n"
        f"🎬 Просмотров за сегодня: **{daily_creations}**\n"
        f"💳 Поступлений за сегодня: **{daily_payments}** кредитов\n\n"
        "**Команды для управления подписками:**\n"
        "/addsub <email>\n"
        "/listsubs\n"
        "/resetsubs\n\n"
        "**Команды для работы:**\n"
        "/pending - посмотреть список ожидающих запросов\n"
        "/addcredits <id> <сумма> - начислить кредиты\n\n"
        "**Для отправки видео:**\n"
        "Отправь видео в бот с подписью: `/send <ID_запроса>`"
    )
    
    await message.answer(stats_message)

@router.message(Command("addsub"))
async def add_subscription_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    email = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if not email:
        await message.answer("Пожалуйста, укажите почту: /addsub <email>")
        return
    
    success = await add_subscription(email)
    
    if success:
        await message.answer(f"Почта `{email}` успешно добавлена в пул подписок.")
    else:
        await message.answer(f"Ошибка: Почта `{email}` уже существует в базе данных.")

@router.message(Command("listsubs"))
async def list_subscriptions_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    subscriptions = await get_all_subscriptions()
    
    if not subscriptions:
        await message.answer("Пул подписок пуст. Добавьте почты с помощью /addsub.")
        return
        
    stats_message = "📧 **Пул подписок:**\n\n"
    for email, usage, limit in subscriptions:
        stats_message += f"`{email}`: {usage} из {limit} использований\n"
        
    await message.answer(stats_message)

@router.message(Command("resetsubs"))
async def reset_subscriptions_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return
    
    await reset_all_subscriptions()
    await message.answer("Счётчики использования всех подписок сброшены.")

@router.message(Command("pending"))
async def show_pending_requests_handler(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        return

    requests = await get_pending_requests()
    
    if not requests:
        await message.answer("Список ожидающих запросов пуст.")
        return

    requests_message = "📝 **Ожидающие запросы:**\n\n"
    for request_id, user_id, prompt, type in requests:
        requests_message += f"**ID запроса:** `{request_id}`\n"
        requests_message += f"**ID пользователя:** `{user_id}`\n"
        requests_message += f"**Тип:** `{type}`\n"
        requests_message += f"**Промт:** `{prompt}`\n\n"
    
    await message.answer(requests_message)

@router.message(F.from_user.id == ADMIN_ID, F.video)
async def send_video_handler(message: Message) -> None:
    command_text = message.caption
    
    if command_text and command_text.startswith('/send'):
        try:
            request_id = int(command_text.split()[1])
            pending_requests = await get_pending_requests()
            
            user_id = None
            for req_id, req_user_id, _, _ in pending_requests:
                if req_id == request_id:
                    user_id = req_user_id
                    break
            
            if user_id:
                await message.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                await message.answer(f"Видео успешно отправлено пользователю `{user_id}`.")
                await delete_pending_request(request_id)
            else:
                await message.answer(f"Запрос с ID `{request_id}` не найден.")

        except (ValueError, IndexError):
            await message.answer("Ошибка в команде. Используйте формат: `/send ID_запроса`")
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
        await message.answer(f"Начислено **{amount}** кредитов пользователю `{user_id}`.")
    except (ValueError, IndexError):
        await message.answer("Ошибка в команде. Используйте формат: `/addcredits ID_пользователя сумма`")