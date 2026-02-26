from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

# Импорты из нашего проекта
import sys
import os
from pathlib import Path

# Добавляем пути для импортов
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "bot"))

from db.database import get_db
from db.models import WorkType, UrgencyLevel, OrderStatus
from services.db_service import UserService, OrderService, BonusService

app = FastAPI(title="NGUEU Helper API", version="1.0.0")

# Настройка CORS для MiniApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SCHEMAS ──────────────────────────────────────────────────

class OrderCreate(BaseModel):
    client_id: int
    work_type: str
    subject: str
    topic: str
    teacher: Optional[str] = None
    requirements: Optional[str] = None
    antiplagiat_percent: Optional[int] = None
    deadline: Optional[str] = None # Будет распарсено в datetime
    urgency: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    username: Optional[str]
    role: str
    bonus_balance: float
    loyalty_level: str
    total_spent: float

# ── ENDPOINTS ────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now()}

@app.get("/api/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int):
    user = await UserService.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "bonus_balance": float(user.bonus_balance),
        "loyalty_level": user.loyalty_level,
        "total_spent": float(user.total_spent)
    }

@app.post("/api/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate):
    try:
        # Парсим дату если она пришла
        deadline_dt = None
        if order_data.deadline:
            deadline_dt = datetime.fromisoformat(order_data.deadline)
            
        order = await OrderService.create(
            client_id=order_data.client_id,
            work_type=order_data.work_type,
            subject=order_data.subject,
            topic=order_data.topic,
            teacher=order_data.teacher,
            requirements=order_data.requirements,
            antiplagiat_percent=order_data.antiplagiat_percent,
            deadline=deadline_dt,
            urgency=order_data.urgency
        )
        return {"status": "success", "order_id": order.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании заказа")

@app.get("/api/orders/client/{client_id}")
async def get_client_orders(client_id: int):
    orders = await OrderService.get_client_orders(client_id)
    return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
