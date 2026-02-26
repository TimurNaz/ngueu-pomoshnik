"""
backend/bot/services/db_service.py
====================================
Сервисный слой — вся бизнес-логика работы с БД.

Содержит сервисы:
  UserService      — пользователи, лояльность, бонусная карта
  ReferralService  — реферальная программа
  OrderService     — заявки
  BonusService     — начисления/списания бонусов
  HolidayService   — праздничные начисления
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


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def _generate_referral_code(length: int = 8) -> str:
    """Генерирует уникальный реферальный код из букв и цифр."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


# ──────────────────────────────────────────────────────────────
# USER SERVICE
# ──────────────────────────────────────────────────────────────

class UserService:

    @staticmethod
    async def get_or_create(
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        referral_code: Optional[str] = None,
    ) -> tuple[User, bool]:
        """
        Получить или создать пользователя.
        Возвращает (user, is_new).
        При создании:
          - начисляет 500 ₽ регистрационный бонус
          - привязывает реферера (если передан referral_code)
          - генерирует собственный реферальный код
        """
        async with async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.id == telegram_id)
                )
                user = result.scalar_one_or_none()

                if user:
                    # Обновляем данные профиля если изменились
                    changed = False
                    if username and user.username != username:
                        user.username = username
                        changed = True
                    if first_name and user.first_name != first_name:
                        user.first_name = first_name
                        changed = True
                    if last_name and user.last_name != last_name:
                        user.last_name = last_name
                        changed = True
                    if changed:
                        await session.commit()
                    return user, False

                # Новый пользователь
                # Генерируем уникальный реферальный код
                while True:
                    code = _generate_referral_code()
                    exists = await session.execute(
                        select(User).where(User.referral_code == code)
                    )
                    if not exists.scalar_one_or_none():
                        break

                user = User(
                    id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    referral_code=code,
                    bonus_balance=Decimal(REGISTRATION_BONUS),
                    loyalty_level=LoyaltyLevel.novice,
                    cashback_percent=0.0,
                )
                session.add(user)
                await session.flush()  # получаем id до commit

                # Записываем регистрационный бонус в историю
                reg_tx = BonusTransaction(
                    user_id=telegram_id,
                    amount=Decimal(REGISTRATION_BONUS),
                    type=BonusType.registration,
                    description=f"Приветственный бонус за регистрацию",
                )
                session.add(reg_tx)

                # Привязываем реферера
                if referral_code:
                    ref_result = await session.execute(
                        select(User).where(User.referral_code == referral_code)
                    )
                    referrer = ref_result.scalar_one_or_none()
                    if referrer and referrer.id != telegram_id:
                        user.referred_by_id = referrer.id
                        referral = Referral(
                            referrer_id=referrer.id,
                            referred_id=telegram_id,
                            status=ReferralStatus.pending,
                        )
                        session.add(referral)

                await session.commit()
                await session.refresh(user)
                logger.info(f"Создан новый пользователь: {telegram_id}")
                return user, True

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Ошибка get_or_create_user: {e}")
                raise

    @staticmethod
    async def get_by_id(telegram_id: int) -> Optional[User]:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == telegram_id)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_by_referral_code(code: str) -> Optional[User]:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.referral_code == code)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update_loyalty(session: AsyncSession, user: User) -> None:
        """
        Пересчитать уровень лояльности и процент кэшбека
        на основе total_spent. Вызывается после каждой оплаты.
        """
        new_level = calculate_loyalty_level(float(user.total_spent))
        new_cashback = CASHBACK_RATES[new_level]

        if user.loyalty_level != new_level or user.cashback_percent != new_cashback:
            user.loyalty_level = new_level
            user.cashback_percent = new_cashback
            logger.info(
                f"Пользователь {user.id}: уровень → {new_level}, "
                f"кэшбек → {new_cashback * 100:.0f}%"
            )

    @staticmethod
    async def get_referral_link(telegram_id: int, bot_username: str) -> str:
        """Получить реферальную ссылку пользователя."""
        user = await UserService.get_by_id(telegram_id)
        if not user or not user.referral_code:
            return ""
        return f"https://t.me/{bot_username}?start=ref_{user.referral_code}"

    @staticmethod
    async def get_referral_stats(telegram_id: int) -> dict:
        """Статистика реферальной программы для личного кабинета."""
        async with async_session() as session:
            # Количество приглашённых
            total = await session.execute(
                select(func.count(Referral.id)).where(
                    Referral.referrer_id == telegram_id
                )
            )
            # Активированные (купившие)
            activated = await session.execute(
                select(func.count(Referral.id)).where(
                    Referral.referrer_id == telegram_id,
                    Referral.status == ReferralStatus.activated,
                )
            )
            user = await session.get(User, telegram_id)
            return {
                "total_invited":  total.scalar() or 0,
                "total_bought":   activated.scalar() or 0,
                "bonus_earned":   float(user.referral_bonus_total) if user else 0,
            }


# ──────────────────────────────────────────────────────────────
# BONUS SERVICE
# ──────────────────────────────────────────────────────────────

class BonusService:

    @staticmethod
    async def add(
        session: AsyncSession,
        user: User,
        amount: Decimal,
        bonus_type: BonusType,
        description: str,
        order_id: Optional[int] = None,
    ) -> BonusTransaction:
        """Начислить бонусы пользователю."""
        user.bonus_balance += amount
        tx = BonusTransaction(
            user_id=user.id,
            amount=amount,
            type=bonus_type,
            description=description,
            related_order_id=order_id,
        )
        session.add(tx)
        logger.info(f"Бонус +{amount}₽ → user={user.id} [{bonus_type}]")
        return tx

    @staticmethod
    async def spend(
        session: AsyncSession,
        user: User,
        order: "Order",
        bonus_amount: Decimal,
    ) -> Decimal:
        """
        Списать бонусы при оплате заказа.
        Максимум MAX_BONUS_RATIO от суммы заказа.
        Возвращает фактически списанную сумму.
        """
        max_allowed = (order.price * Decimal(str(MAX_BONUS_RATIO))).quantize(Decimal("0.01"))
        actual = min(bonus_amount, max_allowed, user.bonus_balance)

        if actual <= 0:
            return Decimal("0")

        user.bonus_balance -= actual
        tx = BonusTransaction(
            user_id=user.id,
            amount=-actual,
            type=BonusType.spent,
            description=f"Оплата бонусами заявки #{order.id}",
            related_order_id=order.id,
        )
        session.add(tx)
        logger.info(f"Бонус -{actual}₽ ← user={user.id} на заявку #{order.id}")
        return actual

    @staticmethod
    async def apply_cashback(
        session: AsyncSession,
        user: User,
        order: "Order",
    ) -> Decimal:
        """
        Начислить кэшбек после принятия заявки (только VIP уровень).
        Кэшбек считается от суммы за вычетом использованных бонусов.
        """
        if user.cashback_percent <= 0:
            return Decimal("0")

        base = (order.price - order.bonus_used).quantize(Decimal("0.01"))
        cashback = (base * Decimal(str(user.cashback_percent))).quantize(Decimal("0.01"))

        if cashback <= 0:
            return Decimal("0")

        order.cashback_earned = cashback
        await BonusService.add(
            session=session,
            user=user,
            amount=cashback,
            bonus_type=BonusType.purchase_cashback,
            description=f"Кэшбек {user.cashback_percent*100:.0f}% за заявку #{order.id}",
            order_id=order.id,
        )
        return cashback

    @staticmethod
    async def get_history(user_id: int, limit: int = 20) -> list[BonusTransaction]:
        async with async_session() as session:
            result = await session.execute(
                select(BonusTransaction)
                .where(BonusTransaction.user_id == user_id)
                .order_by(BonusTransaction.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()


# ──────────────────────────────────────────────────────────────
# REFERRAL SERVICE
# ──────────────────────────────────────────────────────────────

class ReferralService:

    @staticmethod
    async def activate_if_first_purchase(session: AsyncSession, user: User) -> None:
        """
        Вызывается после первой успешной оплаты.
        Если пользователь пришёл по реферальной ссылке
        и это его первая покупка — активируем реферал
        и начисляем 100 ₽ рефереру.
        """
        if not user.referred_by_id:
            return

        # Проверяем — есть ли уже выполненные заказы (кроме текущего)
        prev_orders = await session.execute(
            select(func.count(Order.id)).where(
                Order.client_id == user.id,
                Order.status == OrderStatus.done,
            )
        )
        count = prev_orders.scalar() or 0

        # Активируем только при ПЕРВОЙ покупке (count == 1 после текущей)
        if count != 1:
            return

        referral_result = await session.execute(
            select(Referral).where(
                Referral.referrer_id == user.referred_by_id,
                Referral.referred_id == user.id,
                Referral.status == ReferralStatus.pending,
            )
        )
        referral = referral_result.scalar_one_or_none()
        if not referral:
            return

        referral.status = ReferralStatus.activated
        referral.bonus_paid = True
        referral.bonus_paid_at = datetime.now(timezone.utc)

        # Начисляем бонус рефереру
        referrer = await session.get(User, user.referred_by_id)
        if referrer:
            referrer.referral_count += 1
            referrer.referral_bonus_total += Decimal(REFERRAL_BONUS)
            await BonusService.add(
                session=session,
                user=referrer,
                amount=Decimal(REFERRAL_BONUS),
                bonus_type=BonusType.referral,
                description=f"Бонус за приглашённого друга @{user.username or user.id}",
            )
            logger.info(
                f"Реферальный бонус +{REFERRAL_BONUS}₽ → "
                f"referrer={referrer.id} за друга={user.id}"
            )


# ──────────────────────────────────────────────────────────────
# ORDER SERVICE
# ──────────────────────────────────────────────────────────────

class OrderService:

    @staticmethod
    async def create(
        client_id: int,
        work_type: str,
        subject: str,
        topic: str,
        teacher: Optional[str] = None,
        requirements: Optional[str] = None,
        antiplagiat_percent: Optional[int] = None,
        deadline: Optional[datetime] = None,
        urgency: Optional[str] = None,
    ) -> Order:
        """Создать новую заявку."""
        async with async_session() as session:
            try:
                order = Order(
                    client_id=client_id,
                    work_type=WorkType(work_type),
                    subject=subject,
                    topic=topic,
                    teacher=teacher,
                    requirements=requirements,
                    antiplagiat_percent=antiplagiat_percent,
                    deadline=deadline,
                    urgency=UrgencyLevel(urgency) if urgency else None,
                    status=OrderStatus.new,
                    step=0,
                )
                session.add(order)
                await session.commit()
                await session.refresh(order)
                logger.info(f"Создана заявка #{order.id} клиент={client_id}")
                return order
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Ошибка создания заявки: {e}")
                raise

    @staticmethod
    async def assign_executor(order_id: int, executor_id: int, price: Decimal) -> Order:
        """
        Назначить исполнителя и установить цену.
        Рассчитывает комиссию и сумму исполнителю.
        """
        async with async_session() as session:
            try:
                order = await session.get(Order, order_id)
                if not order:
                    raise ValueError(f"Заявка #{order_id} не найдена")

                commission = (price * Decimal(str(COMMISSION_RATE))).quantize(Decimal("0.01"))

                order.executor_id = executor_id
                order.price = price
                order.commission_amount = commission
                order.executor_amount = price - commission
                order.status = OrderStatus.assigned
                order.step = 1
                order.assigned_at = datetime.now(timezone.utc)

                await session.commit()
                await session.refresh(order)
                logger.info(
                    f"Заявка #{order_id}: исполнитель={executor_id}, "
                    f"цена={price}, комиссия={commission}"
                )
                return order
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Ошибка назначения исполнителя: {e}")
                raise

    @staticmethod
    async def start_work(order_id: int) -> Order:
        """Исполнитель взял заявку в работу."""
        async with async_session() as session:
            order = await session.get(Order, order_id)
            order.status = OrderStatus.in_progress
            order.step = 2
            await session.commit()
            return order

    @staticmethod
    async def send_for_review(order_id: int) -> Order:
        """Исполнитель отправил работу на проверку клиенту."""
        async with async_session() as session:
            order = await session.get(Order, order_id)
            order.status = OrderStatus.review
            order.step = 3
            await session.commit()
            return order

    @staticmethod
    async def complete(order_id: int, bonus_to_spend: Decimal = Decimal("0")) -> Order:
        """
        Клиент принял работу.
        Полный финансовый цикл:
          1. Списываем бонусы (если указаны)
          2. Фиксируем оплату
          3. Начисляем кэшбек (если VIP)
          4. Обновляем total_spent и уровень лояльности
          5. Активируем реферал (если первая покупка)
        """
        async with async_session() as session:
            try:
                order = await session.get(Order, order_id)
                if not order:
                    raise ValueError(f"Заявка #{order_id} не найдена")

                client = await session.get(User, order.client_id)
                if not client:
                    raise ValueError(f"Клиент не найден")

                # 1. Списываем бонусы
                if bonus_to_spend > 0:
                    actual_spent = await BonusService.spend(session, client, order, bonus_to_spend)
                    order.bonus_used = actual_spent

                # 2. Обновляем total_spent (сумма за вычетом бонусов)
                paid_amount = order.price - order.bonus_used
                client.total_spent += paid_amount

                # 3. Обновляем уровень лояльности
                await UserService.update_loyalty(session, client)

                # 4. Начисляем кэшбек
                await BonusService.apply_cashback(session, client, order)

                # 5. Завершаем заявку
                order.status = OrderStatus.done
                order.completed_at = datetime.now(timezone.utc)

                # 6. Активируем реферал при первой покупке
                await ReferralService.activate_if_first_purchase(session, client)

                await session.commit()
                await session.refresh(order)
                logger.info(
                    f"Заявка #{order_id} завершена. "
                    f"Оплачено={paid_amount}, бонусы={order.bonus_used}, "
                    f"кэшбек={order.cashback_earned}"
                )
                return order

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Ошибка завершения заявки: {e}")
                raise

    @staticmethod
    async def cancel(order_id: int) -> Order:
        """Отменить заявку."""
        async with async_session() as session:
            order = await session.get(Order, order_id)
            order.status = OrderStatus.canceled
            await session.commit()
            return order

    @staticmethod
    async def get_client_orders(
        client_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Order]:
        async with async_session() as session:
            q = select(Order).where(Order.client_id == client_id)
            if status:
                q = q.where(Order.status == OrderStatus(status))
            q = q.order_by(Order.created_at.desc()).limit(limit).offset(offset)
            result = await session.execute(q)
            return result.scalars().all()

    @staticmethod
    async def get_by_id(order_id: int) -> Optional[Order]:
        async with async_session() as session:
            return await session.get(Order, order_id)


# ──────────────────────────────────────────────────────────────
# HOLIDAY BONUS SERVICE
# ──────────────────────────────────────────────────────────────

class HolidayService:

    @staticmethod
    async def create(
        name: str,
        bonus_amount: Decimal,
        trigger_date: datetime,
        target: str = "all",
    ) -> HolidayBonus:
        """Создать праздничное начисление (вызывается из админки)."""
        async with async_session() as session:
            hb = HolidayBonus(
                name=name,
                bonus_amount=bonus_amount,
                target=HolidayTarget(target),
                trigger_date=trigger_date,
                is_active=True,
                is_sent=False,
            )
            session.add(hb)
            await session.commit()
            await session.refresh(hb)
            return hb

    @staticmethod
    async def send_pending() -> int:
        """
        Отправить все не отправленные праздничные бонусы у которых
        trigger_date <= сейчас. Возвращает количество обработанных.
        Запускать по расписанию (например, раз в час).
        """
        now = datetime.now(timezone.utc)
        async with async_session() as session:
            result = await session.execute(
                select(HolidayBonus).where(
                    HolidayBonus.is_active == True,
                    HolidayBonus.is_sent == False,
                    HolidayBonus.trigger_date <= now,
                )
            )
            holidays = result.scalars().all()
            total = 0

            for hb in holidays:
                # Определяем целевых пользователей
                q = select(User).where(User.is_active == True, User.role == UserRole.client)

                if hb.target == HolidayTarget.level_2:
                    q = q.where(User.loyalty_level.in_([
                        LoyaltyLevel.student, LoyaltyLevel.regular, LoyaltyLevel.vip
                    ]))
                elif hb.target == HolidayTarget.level_3:
                    q = q.where(User.loyalty_level.in_([
                        LoyaltyLevel.regular, LoyaltyLevel.vip
                    ]))
                elif hb.target == HolidayTarget.level_4:
                    q = q.where(User.loyalty_level == LoyaltyLevel.vip)

                users_result = await session.execute(q)
                users = users_result.scalars().all()

                for user in users:
                    await BonusService.add(
                        session=session,
                        user=user,
                        amount=hb.bonus_amount,
                        bonus_type=BonusType.holiday,
                        description=f"Праздничный бонус: {hb.name}",
                    )
                    total += 1

                hb.is_sent = True

            await session.commit()
            logger.info(f"Праздничные бонусы отправлены: {len(holidays)} событий, {total} пользователей")
            return total


# ──────────────────────────────────────────────────────────────
# REVIEW SERVICE
# ──────────────────────────────────────────────────────────────

class ReviewService:

    @staticmethod
    async def create(
        order_id: int,
        client_id: int,
        nps_score: int,
        comment: Optional[str] = None,
    ) -> Review:
        async with async_session() as session:
            review = Review(
                order_id=order_id,
                client_id=client_id,
                nps_score=max(1, min(10, nps_score)),
                comment=comment,
                is_published=False,
            )
            session.add(review)
            await session.commit()
            await session.refresh(review)
            return review

    @staticmethod
    async def get_published(limit: int = 10) -> list[Review]:
        async with async_session() as session:
            result = await session.execute(
                select(Review)
                .where(Review.is_published == True)
                .order_by(Review.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
