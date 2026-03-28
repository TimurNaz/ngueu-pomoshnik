import logging
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from db.models import Order, OrderStatus, User, NotificationType
from config import MINIAPP_URL
from services.db_service import NotificationDBService

logger = logging.getLogger(__name__)

def get_order_webapp_url(order_id: int) -> str:
    """Формирует URL для открытия конкретного заказа в MiniApp."""
    base_url = (MINIAPP_URL or "").strip().split()[0] if (MINIAPP_URL or "").strip() else ""
    if not base_url.startswith("https://"):
        return ""
    base_url = base_url.rstrip("/")
    return f"{base_url}/orders/{order_id}"

# Маппинг OrderStatus → NotificationType
STATUS_TO_NOTIF_TYPE = {
    OrderStatus.assigned: NotificationType.executor_assigned,
    OrderStatus.priced: NotificationType.price_set,
    OrderStatus.in_progress: NotificationType.order_in_progress,
    OrderStatus.review: NotificationType.order_review,
    OrderStatus.done: NotificationType.order_done,
    OrderStatus.confirming: NotificationType.order_confirming,
    OrderStatus.completed: NotificationType.order_completed,
    OrderStatus.disputed: NotificationType.order_disputed,
    OrderStatus.canceled: NotificationType.order_canceled,
}

STATUS_MESSAGES = {
    OrderStatus.assigned: ("Исполнитель назначен", "Ваша заявка #{order_id} принята в работу."),
    OrderStatus.priced: ("Цена назначена", "Цена заявки #{order_id} установлена. Перейдите к оплате."),
    OrderStatus.in_progress: ("Заказ в работе", "Исполнитель приступил к выполнению заявки #{order_id}."),
    OrderStatus.review: ("Заказ на проверке", "Работа по заявке #{order_id} выполнена и ожидает вашей проверки."),
    OrderStatus.done: ("Работа готова", "Работа по заявке #{order_id} отправлена вам. Проверьте в течение 2 дней."),
    OrderStatus.confirming: ("Проверьте работу", "У вас 2 дня на проверку работы по заявке #{order_id}."),
    OrderStatus.completed: ("Заказ завершён", "Заявка #{order_id} успешно завершена. Спасибо, что выбрали нас!"),
    OrderStatus.disputed: ("Заявка оспорена", "Заявка #{order_id} передана на рассмотрение администратору."),
    OrderStatus.canceled: ("Заявка отменена", "Ваша заявка #{order_id} была отменена."),
}

class NotificationService:
    @staticmethod
    async def send_order_status_update(bot: Bot, order: Order, client: User, executor: User = None):
        """Отправляет уведомление клиенту об изменении статуса заказа + сохраняет в БД."""
        notif_type = STATUS_TO_NOTIF_TYPE.get(order.status)
        msg_data = STATUS_MESSAGES.get(order.status)

        if not msg_data:
            return

        title, text_template = msg_data
        text = text_template.format(order_id=order.id)

        if executor and order.status == OrderStatus.assigned:
            text += f" Исполнитель: {executor.first_name or executor.username}"

        # Сохраняем в БД
        try:
            await NotificationDBService.create(
                user_id=client.id,
                notif_type=notif_type,
                title=title,
                text=text,
                order_id=order.id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления в БД: {e}")

        # Отправляем в Telegram
        tg_icons = {
            OrderStatus.assigned: "✅",
            OrderStatus.in_progress: "⚙️",
            OrderStatus.review: "👀",
            OrderStatus.done: "🎉",
            OrderStatus.canceled: "❌",
        }
        icon = tg_icons.get(order.status, "📌")
        tg_message = f"{icon} <b>{title}</b>\n\n{text}"

        try:
            builder = InlineKeyboardBuilder()
            webapp_url = get_order_webapp_url(order.id)
            if webapp_url:
                builder.add(InlineKeyboardButton(text="Открыть заказ", web_app=WebAppInfo(url=webapp_url)))
            else:
                builder.add(InlineKeyboardButton(text="Открыть кабинет", callback_data="Personal_account"))

            await bot.send_message(
                chat_id=client.id,
                text=tg_message,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
            logger.info(f"Уведомление о статусе {order.status} отправлено пользователю {client.id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю {client.id}: {e}")

    @staticmethod
    async def notify_new_bonus(bot: Bot, user_id: int, amount: float, reason: str):
        """Отправляет уведомление о начислении бонусов + сохраняет в БД."""
        title = "Начислены баллы"
        text = f"Вам начислено {amount} баллов. {reason}"

        # Сохраняем в БД
        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.bonus,
                title=title,
                text=text,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения бонусного уведомления в БД: {e}")

        # Отправляем в Telegram
        tg_message = (
            f"🎁 <b>Вам начислены бонусы!</b>\n\n"
            f"💰 Сумма: <b>+{amount}</b>\n"
            f"📝 Причина: {reason}\n\n"
            f"Проверьте ваш баланс в личном кабинете."
        )
        try:
            await bot.send_message(chat_id=user_id, text=tg_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка при отправке бонусного уведомления {user_id}: {e}")

    @staticmethod
    async def notify_order_created(user_id: int, order_id: int):
        """Создаёт уведомление о создании заявки (без Telegram — клиент сам создал)."""
        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.order_created,
                title="Заявка создана",
                text=f"Ваша заявка №{order_id} успешно отправлена. Ожидайте подбора исполнителя.",
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления о создании заявки: {e}")

    @staticmethod
    async def notify_payment_success(user_id: int, order_id: int, amount: float):
        """Уведомление об успешной оплате клиенту + исполнителю + админам."""
        title = "Оплата получена"
        text = f"Оплата заказа #{order_id} на сумму {amount:.0f} ₽ прошла успешно. Работа скоро начнётся!"

        # In-app клиенту
        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.payment_success,
                title=title,
                text=text,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления об оплате: {e}")

        # Telegram push клиенту + исполнителю + админам
        try:
            from main import bot
            from config import ADMIN_IDS
            from services.db_service import OrderService

            # Клиенту
            tg_message = f"✅ <b>{title}</b>\n\n{text}"
            builder = InlineKeyboardBuilder()
            webapp_url = get_order_webapp_url(order_id)
            if webapp_url:
                builder.add(InlineKeyboardButton(text="Открыть заказ", web_app=WebAppInfo(url=webapp_url)))
            await bot.send_message(chat_id=user_id, text=tg_message, reply_markup=builder.as_markup(), parse_mode="HTML")

            # Исполнителю
            order = await OrderService.get_by_id(order_id)
            if order and order.executor_id:
                executor_msg = (
                    f"💳 <b>Заказ #{order_id} оплачен!</b>\n\n"
                    f"Сумма: {amount:.0f} ₽\n"
                    f"Можно начинать работу."
                )
                try:
                    await bot.send_message(chat_id=order.executor_id, text=executor_msg, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Ошибка уведомления исполнителя {order.executor_id}: {e}")

            # Админам
            admin_msg = (
                f"💳 <b>Оплата заказа #{order_id}</b>\n\n"
                f"Сумма: {amount:.0f} ₽\n"
                f"Клиент: {user_id}"
            )
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(chat_id=admin_id, text=admin_msg, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Ошибка уведомления админа {admin_id} об оплате: {e}")

        except Exception as e:
            logger.error(f"Ошибка отправки TG-уведомлений об оплате: {e}")

    @staticmethod
    async def notify_payment_refunded(user_id: int, order_id: int, amount: float):
        """Уведомление о возврате средств."""
        title = "Средства возвращены"
        text = f"Возврат {amount:.0f} ₽ по заказу #{order_id} выполнен. Деньги поступят на карту в течение нескольких дней."

        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.payment_refunded,
                title=title,
                text=text,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления о возврате: {e}")

        try:
            from main import bot
            tg_message = f"💸 <b>{title}</b>\n\n{text}"
            await bot.send_message(chat_id=user_id, text=tg_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка отправки TG-уведомления о возврате: {e}")

    @staticmethod
    async def notify_price_set(user_id: int, order_id: int, price: float):
        """Уведомление о назначении цены."""
        title = "Цена назначена"
        text = f"Цена заказа #{order_id} установлена: {price:.0f} ₽. Перейдите к оплате."

        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.price_set,
                title=title,
                text=text,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления о цене: {e}")

        try:
            from main import bot
            tg_message = f"💰 <b>{title}</b>\n\n{text}"
            builder = InlineKeyboardBuilder()
            webapp_url = get_order_webapp_url(order_id)
            if webapp_url:
                builder.add(InlineKeyboardButton(text="Перейти к оплате", web_app=WebAppInfo(url=webapp_url)))
            await bot.send_message(chat_id=user_id, text=tg_message, reply_markup=builder.as_markup(), parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка отправки TG-уведомления о цене: {e}")

    @staticmethod
    async def notify_order_completed(user_id: int, order_id: int):
        """Уведомление о завершении заказа (клиент подтвердил)."""
        title = "Заказ завершён"
        text = f"Заказ #{order_id} успешно завершён. Спасибо, что выбрали нас!"

        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.order_completed,
                title=title,
                text=text,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления о завершении: {e}")

        try:
            from main import bot
            await bot.send_message(chat_id=user_id, text=f"🎉 <b>{title}</b>\n\n{text}", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка отправки TG-уведомления о завершении: {e}")

    @staticmethod
    async def notify_order_disputed(order_id: int, client_id: int, reason: str):
        """Уведомление админам о споре + in-app клиенту."""
        # In-app клиенту
        try:
            await NotificationDBService.create(
                user_id=client_id,
                notif_type=NotificationType.order_disputed,
                title="Заявка на рассмотрении",
                text=f"Ваша заявка #{order_id} передана администратору на рассмотрение.",
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения уведомления о споре: {e}")

        # Push админам
        try:
            from main import bot
            from config import ADMIN_IDS
            from services.db_service import UserService

            client = await UserService.get_by_id(client_id)
            client_name = f"{client.first_name or ''} {client.last_name or ''}".strip() or client.username or f"ID {client_id}"

            admin_msg = (
                f"⚠️ <b>Спор по заказу #{order_id}</b>\n\n"
                f"👤 Клиент: {client_name}\n"
                f"📝 Причина: {reason}\n\n"
                f"Перейдите в админ-панель для разбора."
            )
            for admin_id in ADMIN_IDS:
                try:
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="💸 Возврат 50%", callback_data=f"dispute_refund_{order_id}")],
                        [InlineKeyboardButton(text="❌ Отказ в возврате", callback_data=f"dispute_reject_{order_id}")],
                    ])
                    await bot.send_message(admin_id, admin_msg, reply_markup=markup, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Ошибка уведомления админа {admin_id} о споре: {e}")
        except Exception as e:
            logger.error(f"Ошибка отправки споров админам: {e}")

    @staticmethod
    async def notify_payment_reminder(user_id: int, order_id: int, hours_left: int):
        """Напоминание об оплате."""
        title = "Напоминание об оплате"
        text = f"Не забудьте оплатить заказ #{order_id}. Осталось {hours_left} ч., после чего заказ будет отменён."

        try:
            await NotificationDBService.create(
                user_id=user_id,
                notif_type=NotificationType.payment_reminder,
                title=title,
                text=text,
                order_id=order_id,
            )
        except Exception as e:
            logger.error(f"Ошибка сохранения напоминания: {e}")

        try:
            from main import bot
            tg_message = f"⏰ <b>{title}</b>\n\n{text}"
            builder = InlineKeyboardBuilder()
            webapp_url = get_order_webapp_url(order_id)
            if webapp_url:
                builder.add(InlineKeyboardButton(text="Перейти к оплате", web_app=WebAppInfo(url=webapp_url)))
            await bot.send_message(chat_id=user_id, text=tg_message, reply_markup=builder.as_markup(), parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания: {e}")
