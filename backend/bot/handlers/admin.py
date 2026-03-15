from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from keyboards.client import get_client_back
from services.db_service import OrderService, UserService
from services.notification_service import NotificationService
from db.models import OrderStatus
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(lambda q: q.data == "admin_dashboard")
async def admin_dashboard(query: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Ожидающие (новые)", callback_data="pending_orders")],
        [InlineKeyboardButton(text="👀 На проверке (сданные)", callback_data="review_orders")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]
    ])
    
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media="https://storage.yandexcloud.net/ngueu-bot-images/Personal_account.png",
                caption="🛠 <b>Панель администратора</b>\n\nВыберите раздел для работы с заявками:",
                parse_mode="HTML"
            ),
            reply_markup=markup
        )
    except Exception:
        await query.message.edit_caption(
            caption="🛠 <b>Панель администратора</b>\n\nВыберите раздел для работы с заявками:",
            reply_markup=markup,
            parse_mode="HTML"
        )
    await query.answer()

@router.callback_query(F.data == "pending_orders")
async def show_pending_orders(query: CallbackQuery):
    try:
        orders = await OrderService.get_unassigned()
        if not orders:
            await query.answer("✅ Новых заявок пока нет.", show_alert=True)
            return

        await query.answer()
        await query.message.delete()
        
        await query.message.answer(f"📋 <b>Найдено заявок (новые/ожидание): {len(orders)}</b>")

        for order in orders:
            text = await UserService.format_order_text(order)
            
            # Если исполнитель уже назначен, добавляем инфо об этом
            if order.status == OrderStatus.assigned:
                executor = await UserService.get_by_id(order.executor_id)
                exec_name = f"@{executor.username}" if executor.username else f"ID {executor.id}"
                text = text.replace("📍 <b>Выберите исполнителя:</b>", f"⏳ <b>Ждем подтверждения от:</b> {exec_name}\n\n📍 <b>Переназначить исполнителя:</b>")
            
            markup = await UserService.get_admin_order_markup(order.id)
            
            # Добавляем кнопку возврата
            inline_kb = markup.inline_keyboard
            inline_kb.append([InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")])
            
            await query.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка при загрузке заявок: {e}")
        await query.answer("❌ Ошибка.")

@router.callback_query(F.data == "review_orders")
async def show_review_orders(query: CallbackQuery):
    try:
        from sqlalchemy import select
        from db.database import async_session
        from db.models import Order
        
        async with async_session() as session:
            q = select(Order).where(Order.status == OrderStatus.review)
            result = await session.execute(q)
            orders = result.scalars().all()

        if not orders:
            await query.answer("☕️ Заявок на проверке пока нет.", show_alert=True)
            return

        await query.answer()
        await query.message.delete()
        
        await query.message.answer(f"👀 <b>Заявок ожидают проверки: {len(orders)}</b>")

        for order in orders:
            client = await UserService.get_by_id(order.client_id)
            executor = await UserService.get_by_id(order.executor_id)
            
            text = (
                f"🧐 <b>Проверка заявки #{order.id}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📚 Предмет: {order.subject}\n"
                f"👤 Клиент: {client.first_name or client.username}\n"
                f"👨‍💻 Исполнитель: @{executor.username or executor.id}\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Утвердить и отправить", callback_data=f"admin_approve_{order.id}")],
                [InlineKeyboardButton(text="❌ На доработку", callback_data=f"admin_reject_{order.id}")],
                [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
            ])
            
            await query.message.answer(text, reply_markup=markup)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await query.answer("❌ Ошибка.")

@router.callback_query(F.data.startswith("admin_approve_"))
async def process_admin_approve(query: CallbackQuery):
    order_id = int(query.data.split("_")[-1])
    success = await OrderService.update_status(order_id, OrderStatus.done)
    
    if success:
        order = await OrderService.get_by_id(order_id)
        client = await UserService.get_by_id(order.client_id)
        await NotificationService.send_order_status_update(query.bot, order, client)
        
        # После утверждения даем кнопку возврата
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
        ])
        await query.message.edit_text(f"✅ <b>Заявка #{order_id} успешно закрыта!</b>", reply_markup=markup)
        await query.answer("Завершено!")
    else:
        await query.answer("Ошибка.")

@router.callback_query(F.data.startswith("admin_reject_"))
async def process_admin_reject(query: CallbackQuery):
    order_id = int(query.data.split("_")[-1])
    success = await OrderService.update_status(order_id, OrderStatus.in_progress)
    
    if success:
        order = await OrderService.get_by_id(order_id)
        try: await query.bot.send_message(order.executor_id, f"⚠️ Работа по #{order.id} на доработке.")
        except: pass
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
        ])
        await query.message.edit_text(f"🔄 <b>Заявка #{order_id} возвращена исполнителю.</b>", reply_markup=markup)
        await query.answer("На доработку.")
    else:
        await query.answer("Ошибка.")

@router.callback_query(F.data.startswith("assign_"))
async def process_order_assignment(query: CallbackQuery):
    try:
        parts = query.data.split("_")
        order_id = int(parts[1])
        executor_id = int(parts[2])

        success = await OrderService.assign_executor(order_id, executor_id)
        if success:
            order = await OrderService.get_by_id(order_id)
            executor = await UserService.get_by_id(executor_id)
            client = await UserService.get_by_id(order.client_id)

            # Уведомляем ИСПОЛНИТЕЛЯ (Критично)
            try:
                await query.bot.send_message(
                    chat_id=executor_id,
                    text=(
                        f"🎉 <b>Вам назначена новая заявка #{order.id}!</b>\n\n"
                        f"📚 Предмет: {order.subject}\n"
                        f"📝 Тема: {order.topic}\n\n"
                        f"Перейдите в режим исполнителя, чтобы принять её в работу."
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить исполнителя {executor_id}: {e}")

            # Уведомляем КЛИЕНТА
            if client:
                await NotificationService.send_order_status_update(query.bot, order, client, executor)

            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
            ])
            await query.message.edit_text(f"✅ <b>Заявка #{order_id} успешно назначена!</b>", reply_markup=markup)
            await query.answer("Исполнитель назначен!")
        else:
            await query.answer("Ошибка.")
    except Exception as e:
        logger.error(f"Ошибка при назначении: {e}")
        await query.answer("❌ Ошибка.")

@router.callback_query(F.data.startswith("cancel_order_"))
async def process_order_cancel(query: CallbackQuery):
    order_id = int(query.data.split("_")[-1])
    success = await OrderService.update_status(order_id, OrderStatus.canceled)
    if success:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
        ])
        await query.message.edit_text(f"❌ Заявка #{order_id} отклонена.", reply_markup=markup)
        await query.answer("Отклонена.")
    else:
        await query.answer("Ошибка.")
