"""
backend/bot/services/db_service.py
====================================
Сервисный слой — вся бизнес-логика работы с БД.
"""

import logging
import secrets
import string
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Tuple
from pathlib import Path

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaDocument

from db.models import (
    User, UserRole, LoyaltyLevel, ExecutorProfile,
    Order, OrderStatus, WorkType, UrgencyLevel,
    Payment, PaymentStatus, PaymentStage,
    BonusTransaction, BonusType,
    Referral, ReferralStatus,
    Review, HolidayBonus, HolidayTarget, KnowledgeBase,
    Notification, NotificationType,
    LOYALTY_THRESHOLDS, CASHBACK_RATES,
    REGISTRATION_BONUS, REFERRAL_BONUS,
    COMMISSION_RATE, MAX_BONUS_RATIO,
    calculate_loyalty_level,
)
from db.database import async_session

logger = logging.getLogger(__name__)

def _generate_referral_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

class ExecutorService:
    @staticmethod
    async def get_available() -> List[Tuple[User, ExecutorProfile]]:
        """Возвращает список доступных и проверенных исполнителей."""
        async with async_session() as session:
            query = (
                select(User, ExecutorProfile)
                .join(ExecutorProfile, User.id == ExecutorProfile.user_id)
                .where(
                    User.role == UserRole.executor,
                    User.is_active == True,
                    ExecutorProfile.is_available == True,
                    ExecutorProfile.is_verified == True
                )
            )
            result = await session.execute(query)
            return result.all()

class UserService:
    @staticmethod
    async def get_or_create(telegram_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, referral_code: Optional[str] = None) -> Tuple[User, bool]:
        async with async_session() as session:
            try:
                result = await session.execute(select(User).where(User.id == telegram_id))
                user = result.scalar_one_or_none()
                if user:
                    changed = False
                    if username and user.username != username: user.username = username; changed = True
                    if first_name and user.first_name != first_name: user.first_name = first_name; changed = True
                    if last_name and user.last_name != last_name: user.last_name = last_name; changed = True
                    if changed: await session.commit()
                    return user, False
                
                while True:
                    code = _generate_referral_code()
                    exists = await session.execute(select(User).where(User.referral_code == code))
                    if not exists.scalar_one_or_none(): break
                
                user = User(
                    id=telegram_id, 
                    username=username, 
                    first_name=first_name, 
                    last_name=last_name, 
                    referral_code=code, 
                    bonus_balance=Decimal(REGISTRATION_BONUS), 
                    loyalty_level=LoyaltyLevel.novice, 
                    cashback_percent=0.0
                )
                session.add(user)
                await session.flush()
                
                reg_tx = BonusTransaction(user_id=telegram_id, amount=Decimal(REGISTRATION_BONUS), type=BonusType.registration, description=f"Приветственный бонус за регистрацию")
                session.add(reg_tx)
                
                if referral_code:
                    ref_result = await session.execute(select(User).where(User.referral_code == referral_code))
                    referrer = ref_result.scalar_one_or_none()
                    if referrer and referrer.id != telegram_id:
                        user.referred_by_id = referrer.id
                        referral = Referral(referrer_id=referrer.id, referred_id=telegram_id, status=ReferralStatus.pending)
                        session.add(referral)
                
                await session.commit()
                await session.refresh(user)
                return user, True
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Ошибка UserService: {e}")
                raise

    @staticmethod
    async def get_by_id(telegram_id: int) -> Optional[User]:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == telegram_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def update_loyalty(session: AsyncSession, user: User) -> None:
        new_level = calculate_loyalty_level(float(user.total_spent))
        if user.loyalty_level != new_level:
            user.loyalty_level = new_level
            user.cashback_percent = CASHBACK_RATES[new_level]

    @staticmethod
    async def get_referral_link(telegram_id: int, bot_username: str) -> str:
        user = await UserService.get_by_id(telegram_id)
        return f"https://t.me/{bot_username}?start=ref_{user.referral_code}" if user else ""

    @staticmethod
    async def get_referral_stats(telegram_id: int) -> dict:
        async with async_session() as session:
            total = await session.execute(select(func.count(Referral.id)).where(Referral.referrer_id == telegram_id))
            activated = await session.execute(select(func.count(Referral.id)).where(Referral.referrer_id == telegram_id, Referral.status == ReferralStatus.activated))
            user = await session.get(User, telegram_id)
            return {"total_invited": total.scalar() or 0, "total_bought": activated.scalar() or 0, "bonus_earned": float(user.referral_bonus_total) if user else 0}

    @staticmethod
    async def format_order_text(order: Order) -> str:
        """Форматирует детальный текст заявки для админа, включая имя клиента."""
        client = await UserService.get_by_id(order.client_id)
        client_name = f"{client.first_name or ''} {client.last_name or ''}".strip() or client.username or f"ID {order.client_id}"
        
        return (
            f"🔔 <b>Заявка #{order.id}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Клиент:</b> {client_name} (<a href='tg://user?id={order.client_id}'>{order.client_id}</a>)\n"
            f"📚 <b>Предмет:</b> <code>{order.subject}</code>\n"
            f"📝 <b>Тема:</b> {order.topic}\n"
            f"🛠 <b>Тип:</b> {order.work_type.value}\n"
            f"📅 <b>Срок:</b> {order.deadline.strftime('%d.%m.%Y %H:%M') if order.deadline else 'Не указан'}\n"
            f"🔥 <b>Срочность:</b> {order.urgency.value if order.urgency else 'Не указана'}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>Выберите исполнителя:</b>"
        )

    @staticmethod
    async def get_admin_order_markup(order_id: int) -> InlineKeyboardMarkup:
        """Создает клавиатуру с исполнителями для конкретного заказа."""
        executors = await ExecutorService.get_available()
        keyboard_btns = []
        for u, profile in executors:
            btn_text = f"👤 {u.first_name or u.username} ({profile.rating}⭐)"
            keyboard_btns.append([InlineKeyboardButton(
                text=btn_text, 
                callback_data=f"assign_{order_id}_{u.id}"
            )])
        
        keyboard_btns.append([InlineKeyboardButton(text="❌ Отклонить", callback_data=f"cancel_order_{order_id}")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_btns)

    @staticmethod
    async def send_admin_alert(bot: Bot, order: Order) -> None:
        """Отправляет детальное уведомление админам с файлами и выбором исполнителей."""
        from config import ADMIN_IDS
        if not ADMIN_IDS: return

        text = await UserService.format_order_text(order)
        markup = await UserService.get_admin_order_markup(order.id)

        for admin_id in ADMIN_IDS:
            try:
                admin_user = await UserService.get_by_id(admin_id)
                if not admin_user:
                    continue

                if order.attachments:
                    media = []
                    base_path = Path(__file__).resolve().parent.parent.parent / "static"
                    
                    for i, file_url in enumerate(order.attachments):
                        file_name = file_url.split('/')[-1]
                        file_path = base_path / "uploads" / file_name
                        if not file_path.exists(): continue

                        caption = text if i == 0 else ""
                        ext = file_path.suffix.lower()
                        if ext in ['.png', '.jpg', '.jpeg', '.webp']:
                            media.append(InputMediaPhoto(media=types.FSInputFile(file_path), caption=caption, parse_mode="HTML"))
                        else:
                            media.append(InputMediaDocument(media=types.FSInputFile(file_path), caption=caption, parse_mode="HTML"))
                    
                    if media:
                        await bot.send_media_group(chat_id=admin_id, media=media)
                        await bot.send_message(chat_id=admin_id, text="👇 Назначьте исполнителя для этой заявки:", reply_markup=markup)
                    else:
                        await bot.send_message(admin_id, text, reply_markup=markup)
                else:
                    await bot.send_message(admin_id, text, reply_markup=markup)

            except Exception as e:
                logger.error(f"Не удалось отправить алерт админу {admin_id}: {e}")

class BonusService:
    @staticmethod
    async def add(session: AsyncSession, user: User, amount: Decimal, bonus_type: BonusType, description: str, order_id: Optional[int] = None) -> BonusTransaction:
        user.bonus_balance += amount
        tx = BonusTransaction(user_id=user.id, amount=amount, type=bonus_type, description=description, related_order_id=order_id)
        session.add(tx); return tx

    @staticmethod
    async def spend(session: AsyncSession, user: User, order: "Order", bonus_amount: Decimal) -> Decimal:
        max_allowed = (order.price * Decimal(str(MAX_BONUS_RATIO))).quantize(Decimal("0.01"))
        actual = min(bonus_amount, max_allowed, user.bonus_balance)
        if actual <= 0: return Decimal("0")
        user.bonus_balance -= actual
        tx = BonusTransaction(user_id=user.id, amount=-actual, type=BonusType.spent, description=f"Оплата бонусами заявки #{order.id}", related_order_id=order.id)
        session.add(tx); return actual

    @staticmethod
    async def apply_cashback(session: AsyncSession, user: User, order: "Order") -> Decimal:
        if user.cashback_percent <= 0: return Decimal("0")
        base = (order.price - order.bonus_used).quantize(Decimal("0.01"))
        cashback = (base * Decimal(str(user.cashback_percent))).quantize(Decimal("0.01"))
        if cashback <= 0: return Decimal("0")
        order.cashback_earned = cashback
        await BonusService.add(session, user, cashback, BonusType.purchase_cashback, f"Кэшбек {user.cashback_percent*100:.0f}%", order.id)
        return cashback

    @staticmethod
    async def get_history(user_id: int, limit: int = 20) -> list[BonusTransaction]:
        async with async_session() as session:
            result = await session.execute(select(BonusTransaction).where(BonusTransaction.user_id == user_id).order_by(BonusTransaction.created_at.desc()).limit(limit))
            return result.scalars().all()

class ReferralService:
    @staticmethod
    async def activate_if_first_purchase(session: AsyncSession, user: User) -> None:
        if not user.referred_by_id: return
        prev_orders = await session.execute(select(func.count(Order.id)).where(Order.client_id == user.id, Order.status == OrderStatus.done))
        if prev_orders.scalar() != 1: return
        ref_result = await session.execute(select(Referral).where(Referral.referrer_id == user.referred_by_id, Referral.referred_id == user.id, Referral.status == ReferralStatus.pending))
        referral = ref_result.scalar_one_or_none()
        if not referral: return
        referral.status = ReferralStatus.activated; referral.bonus_paid = True; referral.bonus_paid_at = datetime.now(timezone.utc)
        referrer = await session.get(User, user.referred_by_id)
        if referrer:
            referrer.referral_count += 1; referrer.referral_bonus_total += Decimal(REFERRAL_BONUS)
            await BonusService.add(session, referrer, Decimal(REFERRAL_BONUS), BonusType.referral, f"Бонус за друга @{user.username or user.id}")

class OrderService:
    @staticmethod
    async def create(client_id: int, work_type: str, subject: str, topic: str, teacher: Optional[str] = None, requirements: Optional[str] = None, antiplagiat_percent: Optional[int] = None, deadline: Optional[datetime] = None, urgency: Optional[str] = None, attachments: Optional[list[str]] = None) -> Order:
        async with async_session() as session:
            try:
                u_map = {"3d": "three_days", "three_days": "three_days", "1w": "one_week", "one_week": "one_week", "2w": "two_weeks", "two_weeks": "two_weeks", "1m": "one_month", "one_month": "one_month"}
                clean_urgency = u_map.get(urgency, urgency)
                order = Order(
                    client_id=client_id, work_type=WorkType(work_type), subject=subject, topic=topic, teacher=teacher, requirements=requirements,
                    antiplagiat_percent=antiplagiat_percent, deadline=deadline, urgency=clean_urgency, attachments=attachments or [],
                    status=OrderStatus.new, step=0
                )
                session.add(order); await session.commit(); await session.refresh(order)
                return order
            except Exception as e:
                await session.rollback(); logger.error(f"Ошибка создания заявки: {e}"); raise

    @staticmethod
    async def cancel(order_id: int) -> Order:
        async with async_session() as session:
            order = await session.get(Order, order_id)
            if order:
                order.status = OrderStatus.canceled
                await session.commit(); await session.refresh(order)
            return order

    @staticmethod
    async def get_client_orders(client_id: int, status: Optional[str] = None, limit: int = 20) -> list[Order]:
        async with async_session() as session:
            q = select(Order).where(Order.client_id == client_id)
            if status: q = q.where(Order.status == OrderStatus(status))
            result = await session.execute(q.order_by(Order.created_at.desc()).limit(limit))
            return result.scalars().all()

    @staticmethod
    async def get_unassigned() -> list[Order]:
        """Получает список заказов, требующих внимания админа (status=new или status=assigned)."""
        async with async_session() as session:
            q = (
                select(Order)
                .where(Order.status.in_([OrderStatus.new, OrderStatus.assigned]))
                .order_by(Order.created_at.asc())
            )
            result = await session.execute(q)
            return result.scalars().all()

    @staticmethod
    async def assign_executor(order_id: int, executor_id: int) -> bool:
        """Назначает исполнителя на заказ и меняет статус на assigned."""
        async with async_session() as session:
            try:
                order = await session.get(Order, order_id)
                if not order: return False
                
                order.executor_id = executor_id
                order.status = OrderStatus.assigned
                order.updated_at = datetime.now(timezone.utc)
                
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при назначении исполнителя в БД: {e}")
                return False

    @staticmethod
    async def update_status(order_id: int, new_status: OrderStatus, result_files: Optional[List[str]] = None) -> bool:
        """Универсальный метод обновления статуса заказа."""
        async with async_session() as session:
            try:
                order = await session.get(Order, order_id)
                if not order: return False
                
                order.status = new_status
                if result_files:
                    # Добавляем к существующим или заменяем? Обычно для результата отдельное поле было бы лучше, 
                    # но пока будем использовать attachments или доп. логику
                    order.attachments = list(set((order.attachments or []) + result_files))
                
                order.updated_at = datetime.now(timezone.utc)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при обновлении статуса заказа {order_id}: {e}")
                return False

    @staticmethod
    async def get_executor_orders(executor_id: int, active_only: bool = True) -> list[Order]:
        """Получает список заказов конкретного исполнителя."""
        async with async_session() as session:
            q = select(Order).where(Order.executor_id == executor_id)
            if active_only:
                q = q.where(Order.status.in_([OrderStatus.assigned, OrderStatus.in_progress, OrderStatus.review]))
            result = await session.execute(q.order_by(Order.updated_at.desc()))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(order_id: int) -> Optional[Order]:
        async with async_session() as session: return await session.get(Order, order_id)


class NotificationDBService:
    """Сервис для работы с уведомлениями в БД."""

    @staticmethod
    async def create(user_id: int, notif_type: NotificationType, title: str, text: str, order_id: Optional[int] = None) -> Notification:
        """Создаёт уведомление в БД."""
        async with async_session() as session:
            notif = Notification(
                user_id=user_id,
                type=notif_type,
                title=title,
                text=text,
                order_id=order_id,
            )
            session.add(notif)
            await session.commit()
            await session.refresh(notif)
            return notif

    @staticmethod
    async def get_user_notifications(user_id: int, limit: int = 50) -> list[Notification]:
        """Получает уведомления пользователя."""
        async with async_session() as session:
            result = await session.execute(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    @staticmethod
    async def get_unread_count(user_id: int) -> int:
        """Считает непрочитанные уведомления."""
        async with async_session() as session:
            result = await session.execute(
                select(func.count(Notification.id))
                .where(Notification.user_id == user_id, Notification.is_read == False)
            )
            return result.scalar() or 0

    @staticmethod
    async def mark_read(notification_id: int, user_id: int) -> bool:
        """Помечает одно уведомление как прочитанное."""
        async with async_session() as session:
            notif = await session.get(Notification, notification_id)
            if not notif or notif.user_id != user_id:
                return False
            notif.is_read = True
            await session.commit()
            return True

    @staticmethod
    async def mark_all_read(user_id: int) -> int:
        """Помечает все уведомления пользователя как прочитанные. Возвращает кол-во обновлённых."""
        async with async_session() as session:
            result = await session.execute(
                update(Notification)
                .where(Notification.user_id == user_id, Notification.is_read == False)
                .values(is_read=True)
            )
            await session.commit()
            return result.rowcount
