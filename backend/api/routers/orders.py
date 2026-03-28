import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from api.schemas.order import OrderCreate
from api.schemas.payment import OrderConfirm, OrderDispute
from services.db_service import UserService, OrderService
from services.payment_service import PaymentService
from services.notification_service import NotificationService
from main import bot # Импортируем глобальный экземпляр бота из точки входа бота

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate):
    try:
        deadline_dt = None
        if order_data.deadline:
            date_str = order_data.deadline.replace('Z', '+00:00')
            deadline_dt = datetime.fromisoformat(date_str)
            
        order = await OrderService.create(
            client_id=order_data.client_id,
            work_type=order_data.work_type,
            subject=order_data.subject,
            topic=order_data.topic,
            teacher=order_data.teacher,
            requirements=order_data.requirements,
            antiplagiat_percent=order_data.antiplagiat_percent,
            deadline=deadline_dt,
            urgency=order_data.urgency,
            attachments=order_data.attachments
        )

        try:
            await UserService.send_admin_alert(bot, order)
        except Exception as alert_err:
            logger.error(f"Ошибка при отправке алерта админам: {alert_err}")

        # Создаём in-app уведомление для клиента
        try:
            await NotificationService.notify_order_created(order.client_id, order.id)
        except Exception as notif_err:
            logger.error(f"Ошибка создания уведомления: {notif_err}")

        return {"status": "success", "order_id": order.id}
    except Exception as e:
        logger.error(f"Ошибка в API при создании заказа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{order_id}")
async def get_order_details(order_id: int):
    order = await OrderService.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return order

@router.post("/{order_id}/cancel")
async def cancel_order(order_id: int):
    try:
        order = await OrderService.cancel(order_id)
        
        # Уведомляем админов об отмене клиентом
        try:
            import os
            # Получаем сырую строку, очищаем от кавычек и пробелов
            raw_admins = os.getenv("ADMIN_IDS", "")
            clean_admins = raw_admins.replace("'", "").replace('"', "").strip()
            admin_ids = [int(i.strip()) for i in clean_admins.split(",") if i.strip().isdigit()]
            
            client = await UserService.get_by_id(order.client_id)
            client_name = f"{client.first_name or ''} {client.last_name or ''}".strip() or client.username or f"ID {order.client_id}"
            
            cancel_msg = (
                f"⚠️ <b>Заявка #{order.id} отменена клиентом</b>\n\n"
                f"👤 Клиент: {client_name}\n"
                f"📚 Предмет: {order.subject}\n"
                f"📝 Тема: {order.topic}"
            )
            
            for admin_id in admin_ids:
                try:
                    await bot.send_message(admin_id, cancel_msg, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Ошибка при уведомлении админа {admin_id} об отмене: {e}")
                    
            # Если был назначен исполнитель - уведомляем и его
            if order.executor_id:
                try:
                    await bot.send_message(
                        order.executor_id, 
                        f"❌ <b>Заявка #{order.id} отменена клиентом.</b>\nРабота по ней прекращена.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Ошибка при уведомлении исполнителя {order.executor_id} об отмене: {e}")
                    
        except Exception as notify_err:
            logger.error(f"Общая ошибка при рассылке уведомлений об отмене: {notify_err}")

        return {"status": "success", "new_status": order.status}
    except Exception as e:
        logger.error(f"Ошибка в API при отмене заказа {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/client/{client_id}")
async def get_client_orders(client_id: int):
    return await OrderService.get_client_orders(client_id)

@router.get("/latest/{client_id}")
async def get_latest_orders(client_id: int):
    return await OrderService.get_client_orders(client_id, limit=3)

@router.post("/{order_id}/confirm")
async def confirm_order(order_id: int, data: OrderConfirm):
    """Клиент подтверждает выполненную работу."""
    try:
        result = await PaymentService.confirm_order(order_id, data.user_id)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка подтверждения заказа {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{order_id}/dispute")
async def dispute_order(order_id: int, data: OrderDispute):
    """Клиент оспаривает работу."""
    try:
        result = await PaymentService.dispute_order(order_id, data.user_id, data.reason)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка оспаривания заказа {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
