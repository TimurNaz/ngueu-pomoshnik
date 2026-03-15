import logging
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo
from db.models import Order, OrderStatus, User
from config import MINIAPP_URL

logger = logging.getLogger(__name__)

def get_order_webapp_url(order_id: int) -> str:
    """Формирует URL для открытия конкретного заказа в MiniApp."""
    base_url = (MINIAPP_URL or "").strip().split()[0] if (MINIAPP_URL or "").strip() else ""
    if not base_url.startswith("https://"):
        return ""
    # Удаляем слеш в конце, если он есть
    base_url = base_url.rstrip("/")
    return f"{base_url}/orders/{order_id}"

class NotificationService:
    @staticmethod
    async def send_order_status_update(bot: Bot, order: Order, client: User, executor: User = None):
        """Отправляет уведомление клиенту об изменении статуса заказа."""
        status_messages = {
            OrderStatus.assigned: f"✅ <b>Исполнитель назначен!</b>\n\nВаша заявка #{order.id} принята в работу.",
            OrderStatus.in_progress: f"⚙️ <b>Заказ в работе!</b>\n\nИсполнитель приступил к выполнению заявки #{order.id}.",
            OrderStatus.review: f"👀 <b>Заказ на проверке!</b>\n\nРабота по заявке #{order.id} выполнена и ожидает вашей проверки.",
            OrderStatus.done: f"🎉 <b>Заказ завершен!</b>\n\nЗаявка #{order.id} успешно закрыта. Спасибо, что выбрали нас!",
            OrderStatus.canceled: f"❌ <b>Заявка отменена.</b>\n\nВаша заявка #{order.id} была отменена администратором."
        }

        message = status_messages.get(order.status)
        if not message:
            return

        # Добавляем инфо об исполнителе, если он есть
        if executor and order.status == OrderStatus.assigned:
            message += f"\n\n👤 Исполнитель: {executor.first_name or executor.username}"

        try:
            # Кнопка для быстрого перехода в Mini App
            builder = InlineKeyboardBuilder()
            
            webapp_url = get_order_webapp_url(order.id)
            if webapp_url:
                builder.add(InlineKeyboardButton(text="Открыть заказ", web_app=WebAppInfo(url=webapp_url)))
            else:
                # Фоллбэк на обычную кнопку, если URL не настроен
                builder.add(InlineKeyboardButton(text="Открыть кабинет", callback_data="Personal_account"))
            
            await bot.send_message(
                chat_id=client.id,
                text=message,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
            logger.info(f"Уведомление о статусе {order.status} отправлено пользователю {client.id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю {client.id}: {e}")

    @staticmethod
    async def notify_new_bonus(bot: Bot, user_id: int, amount: float, reason: str):
        """Отправляет уведомление о начислении бонусов."""
        message = (
            f"🎁 <b>Вам начислены бонусы!</b>\n\n"
            f"💰 Сумма: <b>+{amount}</b>\n"
            f"📝 Причина: {reason}\n\n"
            f"Проверьте ваш баланс в личном кабинете."
        )
        try:
            await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка при отправке бонусного уведомления {user_id}: {e}")
