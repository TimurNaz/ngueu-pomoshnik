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
from typing import Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from db.models import (
    User, UserRole, LoyaltyLevel, ExecutorProfile,
    Order, OrderStatus, WorkType, UrgencyLevel,
    Payment, PaymentStatus, PaymentStage,
    BonusTransaction, BonusType,
    Referral, ReferralStatus,
    Review, HolidayBonus, HolidayTarget, KnowledgeBase,
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

class UserService:
    @staticmethod
    async def get_or_create(telegram_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, referral_code: Optional[str] = None) -> tuple[User, bool]:
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
                user = User(id=telegram_id, username=username, first_name=first_name, last_name=last_name, referral_code=code, bonus_balance=Decimal(REGISTRATION_BONUS), loyalty_level=LoyaltyLevel.novice, cashback_percent=0.0)
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
                await session.commit(); await session.refresh(user)
                return user, True
            except SQLAlchemyError as e:
                await session.rollback(); logger.error(f"Ошибка UserService: {e}"); raise

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
    async def create(client_id: int, work_type: str, subject: str, topic: str, teacher: Optional[str] = None, requirements: Optional[str] = None, antiplagiat_percent: Optional[int] = None, deadline: Optional[datetime] = None, urgency: Optional[str] = None) -> Order:
        async with async_session() as session:
            try:
                # МАППИНГ: фронт (короткие) -> база (длинные)
                u_map = {
                    "3d": "three_days", "three_days": "three_days",
                    "1w": "one_week", "one_week": "one_week",
                    "2w": "two_weeks", "two_weeks": "two_weeks",
                    "1m": "one_month", "one_month": "one_month"
                }
                clean_urgency = u_map.get(urgency, urgency)
                
                order = Order(
                    client_id=client_id,
                    work_type=work_type,
                    subject=subject,
                    topic=topic,
                    teacher=teacher,
                    requirements=requirements,
                    antiplagiat_percent=antiplagiat_percent,
                    deadline=deadline,
                    urgency=clean_urgency,
                    status=OrderStatus.new,
                    step=0
                )
                session.add(order); await session.commit(); await session.refresh(order)
                return order
            except Exception as e:
                await session.rollback(); logger.error(f"Ошибка создания заявки: {e}"); raise

    @staticmethod
    async def get_client_orders(client_id: int, status: Optional[str] = None, limit: int = 20) -> list[Order]:
        async with async_session() as session:
            q = select(Order).where(Order.client_id == client_id)
            if status: q = q.where(Order.status == OrderStatus(status))
            result = await session.execute(q.order_by(Order.created_at.desc()).limit(limit))
            return result.scalars().all()

    @staticmethod
    async def get_by_id(order_id: int) -> Optional[Order]:
        async with async_session() as session: return await session.get(Order, order_id)
