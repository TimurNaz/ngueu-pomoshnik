from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from keyboards.client import get_client_back
from services.db_service import OrderService, UserService
from services.payment_service import PaymentService
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
        [InlineKeyboardButton(text="⚠️ Споры", callback_data="disputed_orders")],
        [InlineKeyboardButton(text="💰 Задолженности", callback_data="admin_debts")],
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

    # Переводим в done (работа отправлена клиенту)
    success = await OrderService.update_status(order_id, OrderStatus.done)

    if success:
        order = await OrderService.get_by_id(order_id)
        client = await UserService.get_by_id(order.client_id)

        # Размораживаем первые 50% (за выполненную работу)
        payments = await PaymentService.get_by_order(order_id)
        paid_payment = next((p for p in payments if p.status.value == "paid"), None)
        if paid_payment and paid_payment.frozen_amount:
            # Размораживаем половину замороженного (т.е. 25% от суммы уходит сейчас)
            # По спеке: 50% размораживается при done, остальные 50% при confirming
            # frozen_amount = 50% от суммы. При done мы НЕ размораживаем — ждём подтверждения.
            # Устанавливаем дедлайн подтверждения
            from db.database import async_session
            from db.models import Payment
            from datetime import timedelta, timezone as tz

            async with async_session() as session:
                p = await session.get(Payment, paid_payment.id)
                if p:
                    p.confirmation_deadline = datetime.now(tz.utc) + timedelta(hours=48)
                    await session.commit()

        # Переводим в confirming (2 дня на проверку)
        await OrderService.update_status(order_id, OrderStatus.confirming)

        # Уведомляем клиента
        await NotificationService.send_order_status_update(query.bot, order, client)

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
        ])
        await query.message.edit_text(
            f"✅ <b>Заявка #{order_id} отправлена клиенту!</b>\n"
            f"У клиента 2 дня на проверку.",
            reply_markup=markup,
            parse_mode="HTML"
        )
        await query.answer("Отправлено клиенту!")
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


# ── Споры (disputed) ──────────────────────────────────────────

@router.callback_query(F.data == "disputed_orders")
async def show_disputed_orders(query: CallbackQuery):
    """Список заказов со статусом disputed."""
    try:
        from sqlalchemy import select
        from db.database import async_session
        from db.models import Order

        async with async_session() as session:
            q = select(Order).where(Order.status == OrderStatus.disputed)
            result = await session.execute(q)
            orders = result.scalars().all()

        if not orders:
            await query.answer("✅ Споров нет.", show_alert=True)
            return

        await query.answer()
        await query.message.delete()
        await query.message.answer(f"⚠️ <b>Споры: {len(orders)}</b>", parse_mode="HTML")

        for order in orders:
            client = await UserService.get_by_id(order.client_id)
            client_name = f"{client.first_name or ''} {client.last_name or ''}".strip() or client.username or f"ID {order.client_id}"

            text = (
                f"⚠️ <b>Спор по заказу #{order.id}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📚 Предмет: {order.subject}\n"
                f"👤 Клиент: {client_name}\n"
                f"💰 Цена: {float(order.price or 0):.0f} ₽\n"
                f"━━━━━━━━━━━━━━━━━━"
            )

            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💸 Возврат 50% клиенту", callback_data=f"dispute_refund_{order.id}")],
                [InlineKeyboardButton(text="❌ Отказ в возврате", callback_data=f"dispute_reject_{order.id}")],
                [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")],
            ])
            await query.message.answer(text, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка загрузки споров: {e}")
        await query.answer("❌ Ошибка.")


@router.callback_query(F.data.startswith("dispute_refund_"))
async def process_dispute_refund(query: CallbackQuery):
    """Админ решает: возврат 50% клиенту."""
    order_id = int(query.data.split("_")[-1])
    try:
        # Находим платёж по заказу
        payments = await PaymentService.get_by_order(order_id)
        paid_payment = next((p for p in payments if p.status.value == "paid"), None)

        if not paid_payment:
            await query.answer("Нет оплаченных платежей.", show_alert=True)
            return

        result = await PaymentService.partial_refund(paid_payment.id)

        # Обновляем статус заказа
        await OrderService.update_status(order_id, OrderStatus.completed)

        # Уведомляем клиента
        order = await OrderService.get_by_id(order_id)
        try:
            await NotificationService.notify_payment_refunded(
                user_id=order.client_id,
                order_id=order_id,
                amount=result["refunded_amount"],
            )
        except Exception:
            pass

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
        ])
        await query.message.edit_text(
            f"💸 <b>Возврат по заказу #{order_id} выполнен</b>\n"
            f"Возвращено: {result['refunded_amount']:.0f} ₽",
            reply_markup=markup,
            parse_mode="HTML"
        )
        await query.answer("Возврат выполнен!")
    except Exception as e:
        logger.error(f"Ошибка возврата по спору: {e}")
        await query.answer(f"Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("dispute_reject_"))
async def process_dispute_reject(query: CallbackQuery):
    """Админ решает: отказ в возврате, средства исполнителю."""
    order_id = int(query.data.split("_")[-1])
    try:
        # Размораживаем средства (идут исполнителю)
        payments = await PaymentService.get_by_order(order_id)
        paid_payment = next((p for p in payments if p.status.value == "paid"), None)

        if paid_payment:
            await PaymentService.release_frozen(paid_payment.id)

        await OrderService.update_status(order_id, OrderStatus.completed)

        order = await OrderService.get_by_id(order_id)
        # Уведомляем клиента
        try:
            from services.db_service import NotificationDBService
            from db.models import NotificationType
            await NotificationDBService.create(
                user_id=order.client_id,
                notif_type=NotificationType.order_completed,
                title="Спор закрыт",
                text=f"Администратор рассмотрел спор по заказу #{order_id}. Возврат не одобрен.",
                order_id=order_id,
            )
        except Exception:
            pass

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")]
        ])
        await query.message.edit_text(
            f"❌ <b>Возврат по заказу #{order_id} отклонён</b>\n"
            f"Средства переведены исполнителю.",
            reply_markup=markup,
            parse_mode="HTML"
        )
        await query.answer("Спор закрыт.")
    except Exception as e:
        logger.error(f"Ошибка отклонения спора: {e}")
        await query.answer("Ошибка.", show_alert=True)


# ── Задолженности (debts) ─────────────────────────────────────

@router.callback_query(F.data == "admin_debts")
async def show_debts(query: CallbackQuery):
    """Показать невыплаченные суммы исполнителям."""
    try:
        from sqlalchemy import select, and_
        from db.database import async_session
        from db.models import Order, Payment, PaymentStatus

        async with async_session() as session:
            # Все оплаченные заказы, где исполнитель не выплачен
            q = (
                select(Order, Payment)
                .join(Payment, Order.id == Payment.order_id)
                .where(
                    Payment.status == PaymentStatus.paid,
                    Payment.executor_paid == False,
                    Order.executor_id.isnot(None),
                )
                .order_by(Order.id)
            )
            result = await session.execute(q)
            rows = result.all()

        if not rows:
            await query.answer("✅ Задолженностей нет!", show_alert=True)
            return

        await query.answer()

        total_debt = 0
        lines = []
        for order, payment in rows:
            executor = await UserService.get_by_id(order.executor_id)
            exec_name = f"@{executor.username}" if executor and executor.username else f"ID {order.executor_id}"
            amount = float(order.executor_amount or 0)
            total_debt += amount
            lines.append(f"• #{order.id} → {exec_name}: {amount:.0f} ₽")

            # Добавляем кнопку "Выплачено" для каждого платежа
        text = (
            f"💰 <b>Задолженности исполнителям</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(lines) + "\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Итого: {total_debt:.0f} ₽</b>"
        )

        btns = []
        for order, payment in rows:
            btns.append([InlineKeyboardButton(
                text=f"✅ Выплачено #{order.id}",
                callback_data=f"mark_paid_{payment.id}"
            )])
        btns.append([InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin_dashboard")])

        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=btns), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка загрузки задолженностей: {e}")
        await query.answer("❌ Ошибка.")


@router.callback_query(F.data.startswith("mark_paid_"))
async def mark_executor_paid(query: CallbackQuery):
    """Админ отмечает, что выплатил исполнителю."""
    payment_id = int(query.data.split("_")[-1])
    try:
        from db.database import async_session
        from db.models import Payment

        async with async_session() as session:
            payment = await session.get(Payment, payment_id)
            if not payment:
                await query.answer("Платёж не найден.", show_alert=True)
                return

            payment.executor_paid = True
            payment.executor_paid_at = datetime.now()
            await session.commit()

        await query.answer("✅ Отмечено как выплаченное!", show_alert=True)

        # Обновляем список
        await show_debts(query)

    except Exception as e:
        logger.error(f"Ошибка отметки выплаты: {e}")
        await query.answer("Ошибка.")
