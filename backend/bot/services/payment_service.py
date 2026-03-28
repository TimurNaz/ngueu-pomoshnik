"""
backend/bot/services/payment_service.py
========================================
Бизнес-логика платежей: инициация, webhook, отмена, заморозка/разморозка.
"""

import logging
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session
from db.models import (
    Order, OrderStatus,
    Payment, PaymentStatus, PaymentStage,
    User, BonusType,
    COMMISSION_RATE, MAX_BONUS_RATIO,
)
from services.payment_provider import PaymentProvider
from services.providers import get_provider
from config import PAYMENT_PROVIDER, PAYMENT_RETURN_URL

logger = logging.getLogger(__name__)

# Настраиваемые интервалы
CANCEL_WINDOW_HOURS = 1
PAYMENT_DEADLINE_HOURS = 48
CONFIRMATION_DEADLINE_HOURS = 48


class PaymentService:
    """Сервис платежей. Статические методы — в стиле проекта."""

    @staticmethod
    def _get_provider() -> PaymentProvider:
        return get_provider(PAYMENT_PROVIDER)

    @staticmethod
    async def initiate_payment(
        order_id: int,
        user_id: int,
        bonus_amount: Decimal = Decimal("0"),
    ) -> dict:
        """
        Инициировать оплату заказа.

        1. Валидация: заказ в статусе priced, принадлежит user_id
        2. Списание бонусов (макс 50% от цены)
        3. Создание Payment (status=pending)
        4. Вызов провайдера → получение URL
        5. Возврат {payment_id, confirmation_url, amount, bonus_used}
        """
        from services.db_service import BonusService, UserService

        async with async_session() as session:
            order = await session.get(Order, order_id)
            if not order:
                raise ValueError("Заказ не найден")
            if order.client_id != user_id:
                raise PermissionError("Нельзя оплатить чужой заказ")
            if order.status == OrderStatus.paid:
                raise ValueError("Заказ уже оплачен")
            if order.status != OrderStatus.priced:
                raise ValueError(f"Заказ в статусе '{order.status.value}', оплата невозможна")
            if not order.price or order.price <= 0:
                raise ValueError("Цена заказа не установлена")

            # Отменяем предыдущие pending-платежи по этому заказу
            existing = await session.execute(
                select(Payment).where(
                    Payment.order_id == order_id,
                    Payment.status == PaymentStatus.pending,
                )
            )
            for old_payment in existing.scalars().all():
                old_payment.status = PaymentStatus.canceled
                # Возвращаем бонусы от старого платежа
                if old_payment.bonus_used and old_payment.bonus_used > 0:
                    user_for_refund = await session.get(User, user_id)
                    if user_for_refund:
                        await BonusService.add(
                            session, user_for_refund, old_payment.bonus_used,
                            BonusType.manual,
                            f"Возврат бонусов: отмена pending-платежа заказа #{order_id}",
                            order_id,
                        )
                        order.bonus_used = Decimal("0")

            user = await session.get(User, user_id)
            if not user:
                raise ValueError("Пользователь не найден")

            # Списание бонусов
            actual_bonus = Decimal("0")
            if bonus_amount > 0:
                actual_bonus = await BonusService.spend(session, user, order, bonus_amount)
                order.bonus_used = actual_bonus

            # Сумма к оплате
            pay_amount = (order.price - actual_bonus).quantize(Decimal("0.01"))
            if pay_amount < 0:
                pay_amount = Decimal("0")

            # Финансовые поля заказа
            order.commission_amount = (order.price * Decimal(str(COMMISSION_RATE))).quantize(Decimal("0.01"))
            order.executor_amount = (order.price - order.commission_amount).quantize(Decimal("0.01"))

            # Создаём запись Payment
            payment = Payment(
                order_id=order.id,
                user_id=user_id,
                amount=pay_amount,
                status=PaymentStatus.pending,
                stage=PaymentStage.prepayment,
                provider_name=PAYMENT_PROVIDER,
                bonus_used=actual_bonus,
            )
            session.add(payment)
            await session.flush()

            # Вызов провайдера
            provider = PaymentService._get_provider()

            if pay_amount > 0:
                result = await provider.create_payment(
                    amount=pay_amount,
                    description=f"Оплата заказа #{order.id}",
                    order_id=order.id,
                    return_url=PAYMENT_RETURN_URL,
                )
                payment.provider_payment_id = result.provider_payment_id

                if PAYMENT_PROVIDER == "mock":
                    # Mock: мгновенная оплата без редиректа
                    now = datetime.now(timezone.utc)
                    payment.status = PaymentStatus.paid
                    payment.paid_at = now
                    payment.frozen_amount = (pay_amount * Decimal("0.5")).quantize(Decimal("0.01"))
                    payment.released_amount = Decimal("0")
                    payment.cancel_deadline = now + timedelta(hours=CANCEL_WINDOW_HOURS)
                    order.status = OrderStatus.paid
                    order.paid_at = now

                    # Кэшбек
                    if user:
                        await BonusService.apply_cashback(session, user, order)
                        user.total_spent += order.price
                        await UserService.update_loyalty(session, user)

                    confirmation_url = None
                else:
                    confirmation_url = result.confirmation_url
            elif pay_amount <= 0:
                # Полностью оплачен бонусами — сразу помечаем как paid
                payment.provider_payment_id = f"bonus_only_{order.id}"
                payment.status = PaymentStatus.paid
                payment.paid_at = datetime.now(timezone.utc)
                payment.frozen_amount = Decimal("0")
                payment.cancel_deadline = datetime.now(timezone.utc) + timedelta(hours=CANCEL_WINDOW_HOURS)
                order.status = OrderStatus.paid
                order.paid_at = datetime.now(timezone.utc)
                confirmation_url = None

            await session.commit()
            await session.refresh(payment)

            # Уведомление при мгновенной оплате (mock / бонусы)
            if confirmation_url is None and order.status == OrderStatus.paid:
                try:
                    from services.notification_service import NotificationService
                    await NotificationService.notify_payment_success(
                        user_id=user_id,
                        order_id=order.id,
                        amount=float(pay_amount),
                    )
                except Exception as e:
                    logger.error(f"Ошибка уведомления об оплате: {e}")

            return {
                "payment_id": payment.id,
                "confirmation_url": confirmation_url,
                "amount": float(pay_amount),
                "bonus_used": float(actual_bonus),
            }

    @staticmethod
    async def handle_webhook(
        provider_payment_id: str,
        status: str,
    ) -> None:
        """
        Обработка webhook от провайдера.

        succeeded → Payment.paid, Order.paid, заморозка 50%, cashback
        failed/canceled → Payment.canceled, возврат бонусов
        """
        from services.db_service import BonusService, UserService

        async with async_session() as session:
            result = await session.execute(
                select(Payment).where(Payment.provider_payment_id == provider_payment_id)
            )
            payment = result.scalar_one_or_none()
            if not payment:
                logger.warning(f"Webhook: платёж не найден для provider_id={provider_payment_id}")
                return

            # Идемпотентность
            if payment.status in (PaymentStatus.paid, PaymentStatus.refunded):
                logger.info(f"Webhook: платёж {payment.id} уже в статусе {payment.status.value}, пропуск")
                return

            order = await session.get(Order, payment.order_id)
            user = await session.get(User, payment.user_id)
            now = datetime.now(timezone.utc)

            if status in ("succeeded", "paid"):
                payment.status = PaymentStatus.paid
                payment.paid_at = now
                payment.frozen_amount = (payment.amount * Decimal("0.5")).quantize(Decimal("0.01"))
                payment.released_amount = Decimal("0")
                payment.cancel_deadline = now + timedelta(hours=CANCEL_WINDOW_HOURS)

                order.status = OrderStatus.paid
                order.paid_at = now

                # Кэшбек для VIP
                if user:
                    await BonusService.apply_cashback(session, user, order)
                    user.total_spent += order.price
                    await UserService.update_loyalty(session, user)

                await session.commit()

                # Уведомления (вне транзакции)
                try:
                    from services.notification_service import NotificationService
                    await NotificationService.notify_payment_success(
                        user_id=payment.user_id,
                        order_id=order.id,
                        amount=float(payment.amount),
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления об оплате: {e}")

            elif status in ("failed", "canceled"):
                payment.status = PaymentStatus.canceled

                # Возврат бонусов
                if payment.bonus_used and payment.bonus_used > 0 and user:
                    await BonusService.add(
                        session, user, payment.bonus_used,
                        BonusType.manual,
                        f"Возврат бонусов: оплата заказа #{order.id} не прошла",
                        order.id,
                    )
                    order.bonus_used = Decimal("0")

                await session.commit()
            else:
                logger.warning(f"Webhook: неизвестный статус '{status}' для платежа {payment.id}")

    @staticmethod
    async def cancel_payment(payment_id: int, user_id: int) -> dict:
        """
        Отмена оплаченного платежа в окне 1 час.

        1. Проверка cancel_deadline
        2. Refund 100% через провайдера
        3. Возврат бонусов
        """
        from services.db_service import BonusService

        async with async_session() as session:
            payment = await session.get(Payment, payment_id)
            if not payment:
                raise ValueError("Платёж не найден")
            if payment.user_id != user_id:
                raise PermissionError("Нельзя отменить чужой платёж")
            if payment.status != PaymentStatus.paid:
                raise ValueError("Платёж не в статусе 'оплачен'")

            now = datetime.now(timezone.utc)
            if payment.cancel_deadline and now > payment.cancel_deadline:
                raise ValueError("Время для отмены истекло (1 час)")

            order = await session.get(Order, payment.order_id)
            user = await session.get(User, payment.user_id)

            # Возврат через провайдера
            if payment.amount > 0 and payment.provider_payment_id:
                provider = PaymentService._get_provider()
                await provider.refund(payment.provider_payment_id, payment.amount)

            payment.status = PaymentStatus.refunded
            payment.refunded_amount = payment.amount
            payment.frozen_amount = Decimal("0")
            payment.released_amount = Decimal("0")

            order.status = OrderStatus.canceled

            # Возврат бонусов
            bonus_returned = Decimal("0")
            if payment.bonus_used and payment.bonus_used > 0 and user:
                await BonusService.add(
                    session, user, payment.bonus_used,
                    BonusType.manual,
                    f"Возврат бонусов при отмене заказа #{order.id}",
                    order.id,
                )
                bonus_returned = payment.bonus_used
                order.bonus_used = Decimal("0")

            await session.commit()

            return {
                "status": "refunded",
                "refunded_amount": float(payment.refunded_amount),
                "bonus_returned": float(bonus_returned),
            }

    @staticmethod
    async def release_frozen(payment_id: int) -> None:
        """Разморозить 50% — при подтверждении клиентом или авто через 2 дня."""
        async with async_session() as session:
            payment = await session.get(Payment, payment_id)
            if not payment or payment.status != PaymentStatus.paid:
                return
            if payment.frozen_amount and payment.frozen_amount > 0:
                payment.released_amount = (
                    (payment.released_amount or Decimal("0")) + payment.frozen_amount
                )
                payment.frozen_amount = Decimal("0")
                await session.commit()

    @staticmethod
    async def partial_refund(payment_id: int) -> dict:
        """Возврат замороженных 50% — вызывается админом при disputed."""
        async with async_session() as session:
            payment = await session.get(Payment, payment_id)
            if not payment or payment.status != PaymentStatus.paid:
                raise ValueError("Платёж не найден или не оплачен")
            if not payment.frozen_amount or payment.frozen_amount <= 0:
                raise ValueError("Нет замороженных средств для возврата")

            refund_amount = payment.frozen_amount

            if payment.provider_payment_id and payment.amount > 0:
                provider = PaymentService._get_provider()
                await provider.refund(payment.provider_payment_id, refund_amount)

            payment.refunded_amount = (
                (payment.refunded_amount or Decimal("0")) + refund_amount
            )
            payment.frozen_amount = Decimal("0")

            await session.commit()

            return {
                "status": "partial_refund",
                "refunded_amount": float(payment.refunded_amount),
            }

    @staticmethod
    async def confirm_order(order_id: int, user_id: int) -> dict:
        """
        Клиент подтверждает работу. Размораживает 50% → исполнителю.
        Order.status → completed.
        """
        async with async_session() as session:
            order = await session.get(Order, order_id)
            if not order:
                raise ValueError("Заказ не найден")
            if order.client_id != user_id:
                raise PermissionError("Нельзя подтвердить чужой заказ")
            if order.status not in (OrderStatus.done, OrderStatus.confirming):
                raise ValueError(f"Заказ в статусе '{order.status.value}', подтверждение невозможно")

            order.status = OrderStatus.completed
            order.confirmed_at = datetime.now(timezone.utc)

            # Размораживаем средства по всем платежам заказа
            result = await session.execute(
                select(Payment).where(
                    Payment.order_id == order_id,
                    Payment.status == PaymentStatus.paid,
                )
            )
            for payment in result.scalars().all():
                if payment.frozen_amount and payment.frozen_amount > 0:
                    payment.released_amount = (
                        (payment.released_amount or Decimal("0")) + payment.frozen_amount
                    )
                    payment.frozen_amount = Decimal("0")

            await session.commit()

            # Уведомление
            try:
                from services.notification_service import NotificationService
                await NotificationService.notify_order_completed(user_id, order_id)
            except Exception as e:
                logger.error(f"Ошибка уведомления о подтверждении: {e}")

            return {"status": "completed"}

    @staticmethod
    async def dispute_order(order_id: int, user_id: int, reason: str) -> dict:
        """
        Клиент оспаривает работу. Order.status → disputed.
        Замороженные средства ждут решения админа.
        """
        async with async_session() as session:
            order = await session.get(Order, order_id)
            if not order:
                raise ValueError("Заказ не найден")
            if order.client_id != user_id:
                raise PermissionError("Нельзя оспорить чужой заказ")
            if order.status not in (OrderStatus.done, OrderStatus.confirming):
                raise ValueError(f"Заказ в статусе '{order.status.value}', спор невозможен")

            order.status = OrderStatus.disputed
            await session.commit()

            # Уведомление админу
            try:
                from services.notification_service import NotificationService
                await NotificationService.notify_order_disputed(
                    order_id=order_id,
                    client_id=user_id,
                    reason=reason,
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления о споре: {e}")

            return {"status": "disputed"}

    @staticmethod
    async def set_price(order_id: int, price: Decimal) -> Order:
        """
        Исполнитель назначает цену. Order.status → priced.
        Рассчитывает commission и executor_amount.
        """
        async with async_session() as session:
            order = await session.get(Order, order_id)
            if not order:
                raise ValueError("Заказ не найден")
            if order.status != OrderStatus.assigned:
                raise ValueError(f"Заказ в статусе '{order.status.value}', назначение цены невозможно")
            if price <= 0:
                raise ValueError("Цена должна быть положительной")

            now = datetime.now(timezone.utc)
            order.price = price
            order.commission_amount = (price * Decimal(str(COMMISSION_RATE))).quantize(Decimal("0.01"))
            order.executor_amount = (price - order.commission_amount).quantize(Decimal("0.01"))
            order.status = OrderStatus.priced
            order.priced_at = now
            order.payment_deadline = now + timedelta(hours=PAYMENT_DEADLINE_HOURS)

            await session.commit()
            await session.refresh(order)

            # Уведомление клиенту
            try:
                from services.notification_service import NotificationService
                await NotificationService.notify_price_set(
                    user_id=order.client_id,
                    order_id=order.id,
                    price=float(price),
                )
            except Exception as e:
                logger.error(f"Ошибка уведомления о цене: {e}")

            return order

    @staticmethod
    async def get_by_order(order_id: int) -> list[Payment]:
        """Получить все платежи по заказу."""
        async with async_session() as session:
            result = await session.execute(
                select(Payment)
                .where(Payment.order_id == order_id)
                .order_by(Payment.created_at.desc())
            )
            return result.scalars().all()
