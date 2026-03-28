"""
backend/bot/services/scheduler_service.py
==========================================
Фоновые задачи: автоотмена, напоминания, автоподтверждение.
Запускается через asyncio в bot/main.py.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from db.database import async_session
from db.models import (
    Order, OrderStatus,
    Payment, PaymentStatus,
)

logger = logging.getLogger(__name__)

# Интервалы проверки (в секундах)
CHECK_INTERVAL = 30 * 60  # 30 минут
FAST_CHECK_INTERVAL = 5 * 60  # 5 минут

# Бизнес-интервалы
PAYMENT_DEADLINE_HOURS = 48
CONFIRMATION_DEADLINE_HOURS = 48
REMINDER_HOURS = [12, 24, 36]  # Через сколько часов после priced_at напоминать


class SchedulerService:
    """Фоновые задачи по расписанию."""

    @staticmethod
    async def check_payment_deadlines():
        """
        Автоотмена: заказы в статусе priced дольше 48 часов → canceled.
        """
        try:
            now = datetime.now(timezone.utc)
            async with async_session() as session:
                q = select(Order).where(
                    Order.status == OrderStatus.priced,
                    Order.payment_deadline.isnot(None),
                    Order.payment_deadline < now,
                )
                result = await session.execute(q)
                expired_orders = result.scalars().all()

                for order in expired_orders:
                    order.status = OrderStatus.canceled
                    logger.info(f"Автоотмена: заказ #{order.id} (не оплачен за 48ч)")

                    # Уведомление клиенту
                    try:
                        from services.notification_service import NotificationService
                        from services.db_service import NotificationDBService
                        from db.models import NotificationType
                        await NotificationDBService.create(
                            user_id=order.client_id,
                            notif_type=NotificationType.order_canceled,
                            title="Заказ отменён",
                            text=f"Заказ #{order.id} автоматически отменён из-за отсутствия оплаты в течение 48 часов.",
                            order_id=order.id,
                        )
                    except Exception as e:
                        logger.error(f"Ошибка уведомления об автоотмене: {e}")

                if expired_orders:
                    await session.commit()
                    logger.info(f"Автоотмена: отменено {len(expired_orders)} заказов")
        except Exception as e:
            logger.error(f"Ошибка check_payment_deadlines: {e}")

    @staticmethod
    async def send_payment_reminders():
        """
        Напоминания: заказы в статусе priced → push через 12ч, 24ч, 36ч.
        """
        try:
            now = datetime.now(timezone.utc)
            async with async_session() as session:
                q = select(Order).where(
                    Order.status == OrderStatus.priced,
                    Order.priced_at.isnot(None),
                )
                result = await session.execute(q)
                orders = result.scalars().all()

                for order in orders:
                    hours_since = (now - order.priced_at).total_seconds() / 3600

                    for reminder_hour in REMINDER_HOURS:
                        # Отправляем если прошло нужное кол-во часов (±30 мин)
                        if abs(hours_since - reminder_hour) < 0.5:
                            hours_left = PAYMENT_DEADLINE_HOURS - int(hours_since)
                            if hours_left < 0:
                                hours_left = 0

                            try:
                                from services.notification_service import NotificationService
                                await NotificationService.notify_payment_reminder(
                                    user_id=order.client_id,
                                    order_id=order.id,
                                    hours_left=hours_left,
                                )
                                logger.info(f"Напоминание: заказ #{order.id}, осталось {hours_left}ч")
                            except Exception as e:
                                logger.error(f"Ошибка напоминания для заказа #{order.id}: {e}")
        except Exception as e:
            logger.error(f"Ошибка send_payment_reminders: {e}")

    @staticmethod
    async def check_confirmation_deadlines():
        """
        Автоподтверждение: заказы в статусе confirming дольше 2 дней → completed.
        Замороженные средства размораживаются.
        """
        try:
            now = datetime.now(timezone.utc)
            async with async_session() as session:
                # Ищем платежи с истёкшим confirmation_deadline
                q = select(Payment).where(
                    Payment.confirmation_deadline.isnot(None),
                    Payment.confirmation_deadline < now,
                    Payment.status == PaymentStatus.paid,
                    Payment.frozen_amount > 0,
                )
                result = await session.execute(q)
                expired_payments = result.scalars().all()

                for payment in expired_payments:
                    order = await session.get(Order, payment.order_id)
                    if not order or order.status != OrderStatus.confirming:
                        continue

                    # Размораживаем средства
                    from decimal import Decimal
                    payment.released_amount = (
                        (payment.released_amount or Decimal("0")) + payment.frozen_amount
                    )
                    payment.frozen_amount = Decimal("0")

                    # Завершаем заказ
                    order.status = OrderStatus.completed
                    order.confirmed_at = now
                    logger.info(f"Автоподтверждение: заказ #{order.id}")

                    # Уведомление
                    try:
                        from services.notification_service import NotificationService
                        await NotificationService.notify_order_completed(
                            user_id=order.client_id,
                            order_id=order.id,
                        )
                    except Exception as e:
                        logger.error(f"Ошибка уведомления об автоподтверждении: {e}")

                if expired_payments:
                    await session.commit()
                    logger.info(f"Автоподтверждение: завершено {len(expired_payments)} заказов")
        except Exception as e:
            logger.error(f"Ошибка check_confirmation_deadlines: {e}")


async def run_scheduler():
    """Основной цикл планировщика. Запускается как фоновая задача."""
    logger.info("Планировщик запущен")

    while True:
        try:
            await SchedulerService.check_payment_deadlines()
            await SchedulerService.send_payment_reminders()
            await SchedulerService.check_confirmation_deadlines()
        except Exception as e:
            logger.error(f"Ошибка в цикле планировщика: {e}")

        await asyncio.sleep(CHECK_INTERVAL)
