import logging
from fastapi import APIRouter, HTTPException

from services.db_service import NotificationDBService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)


@router.get("/{user_id}")
async def get_notifications(user_id: int, limit: int = 50):
    """Список уведомлений пользователя."""
    notifications = await NotificationDBService.get_user_notifications(user_id, limit)
    return [
        {
            "id": n.id,
            "type": n.type.value if hasattr(n.type, "value") else str(n.type),
            "title": n.title,
            "text": n.text,
            "order_id": n.order_id,
            "read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]


@router.get("/{user_id}/unread-count")
async def get_unread_count(user_id: int):
    """Количество непрочитанных уведомлений."""
    count = await NotificationDBService.get_unread_count(user_id)
    return {"count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: int, user_id: int):
    """Пометить уведомление как прочитанное."""
    ok = await NotificationDBService.mark_read(notification_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    return {"status": "success"}


@router.post("/{user_id}/read-all")
async def mark_all_read(user_id: int):
    """Пометить все уведомления как прочитанные."""
    count = await NotificationDBService.mark_all_read(user_id)
    return {"status": "success", "updated": count}
