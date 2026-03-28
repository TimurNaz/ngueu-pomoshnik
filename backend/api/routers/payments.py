import logging
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Request

from api.schemas.payment import PaymentCreate, PaymentCancel
from services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)


@router.post("/create")
async def create_payment(data: PaymentCreate):
    """Инициировать оплату заказа."""
    try:
        result = await PaymentService.initiate_payment(
            order_id=data.order_id,
            user_id=data.user_id,
            bonus_amount=Decimal(str(data.bonus_amount)),
        )
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def payment_webhook(request: Request):
    """
    Webhook от платёжного провайдера.
    Этот эндпоинт ИСКЛЮЧЁН из TG-авторизации (см. auth.py).
    """
    try:
        body = await request.body()
        data = await request.json()

        # Извлекаем данные из тела webhook
        obj = data.get("object", data)
        provider_payment_id = obj.get("id") or data.get("provider_payment_id")
        status_str = obj.get("status") or data.get("status")

        if not provider_payment_id:
            raise HTTPException(status_code=400, detail="Missing payment ID")

        # Проверка подписи webhook
        provider = PaymentService._get_provider()
        headers = dict(request.headers)
        if not await provider.verify_webhook(body, headers):
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

        # Маппинг статусов провайдера → внутренние
        status_map = {
            "succeeded": "succeeded",
            "paid": "succeeded",
            "waiting_for_capture": "succeeded",
            "canceled": "canceled",
            "failed": "failed",
        }
        mapped_status = status_map.get(status_str, status_str)

        await PaymentService.handle_webhook(provider_payment_id, mapped_status)
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        # Возвращаем 200 чтобы провайдер не ретраил
        return {"status": "error", "detail": str(e)}


@router.post("/{payment_id}/cancel")
async def cancel_payment(payment_id: int, data: PaymentCancel):
    """Отмена платежа в окне 1 час."""
    try:
        result = await PaymentService.cancel_payment(payment_id, data.user_id)
        return result
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка отмены платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order/{order_id}")
async def get_order_payments(order_id: int):
    """Получить все платежи по заказу."""
    payments = await PaymentService.get_by_order(order_id)
    return [
        {
            "id": p.id,
            "order_id": p.order_id,
            "amount": float(p.amount),
            "status": p.status.value,
            "stage": p.stage.value,
            "provider_name": p.provider_name,
            "bonus_used": float(p.bonus_used or 0),
            "frozen_amount": float(p.frozen_amount or 0),
            "released_amount": float(p.released_amount or 0),
            "refunded_amount": float(p.refunded_amount or 0),
            "executor_paid": p.executor_paid,
            "cancel_deadline": p.cancel_deadline.isoformat() if p.cancel_deadline else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payments
    ]
