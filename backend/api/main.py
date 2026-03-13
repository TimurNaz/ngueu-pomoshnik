from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
import logging
import uuid
import os
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорты из нашего проекта
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "bot"))

from db.database import get_db
from db.models import WorkType, UrgencyLevel, OrderStatus
from services.db_service import UserService, OrderService, BonusService

app = FastAPI(title="NGUEU Helper API", version="1.1.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем папку со статикой (файлами), чтобы их можно было открывать по ссылке
UPLOAD_DIR = Path("backend/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# ── SCHEMAS ──────────────────────────────────────────────────

class OrderCreate(BaseModel):
    client_id: int
    work_type: str
    subject: str
    topic: str
    teacher: Optional[str] = None
    requirements: Optional[str] = None
    antiplagiat_percent: Optional[int] = None
    deadline: Optional[str] = None
    urgency: Optional[str] = None
    attachments: Optional[List[str]] = []

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

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Проверка размера (30 MB)
    MAX_SIZE = 30 * 1024 * 1024
    
    try:
        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=413, detail="Файл слишком большой (макс. 30Мб)")
        
        # Генерация уникального имени
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'file'
        new_filename = f"{uuid.uuid4()}.{ext}"
        
        # Сохранение
        file_path = UPLOAD_DIR / new_filename
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        logger.info(f"Файл загружен: {file.filename} -> {new_filename}")
        
        return {
            "filename": file.filename,
            "file_url": f"/static/uploads/{new_filename}"
        }
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")

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

@app.get("/api/users/{user_id}/bonuses")
async def get_user_bonus_history(user_id: int):
    return await BonusService.get_history(user_id)

@app.post("/api/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate):
    try:
        # Парсим дату
        deadline_dt = None
        if order_data.deadline:
            date_str = order_data.deadline.replace('Z', '+00:00')
            deadline_dt = datetime.fromisoformat(date_str)
            
        logger.info(f"Создание заказа для {order_data.client_id}, файлы: {len(order_data.attachments)}")
        
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
        return {"status": "success", "order_id": order.id}
    except Exception as e:
        logger.error(f"Ошибка в API при создании заказа: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{order_id}")
async def get_order_details(order_id: int):
    order = await OrderService.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return order

@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: int):
    try:
        order = await OrderService.cancel(order_id)
        return {"status": "success", "new_status": order.status}
    except Exception as e:
        logger.error(f"Ошибка при отмене заказа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/latest/{client_id}")
async def get_latest_orders(client_id: int):
    return await OrderService.get_client_orders(client_id, limit=3)

@app.get("/api/orders/client/{client_id}")
async def get_client_orders(client_id: int):
    return await OrderService.get_client_orders(client_id)

@app.get("/api/users/{user_id}/referral")
async def get_user_referral(user_id: int):
    bot_username = "NGU_StudBot" 
    link = await UserService.get_referral_link(user_id, bot_username)
    stats = await UserService.get_referral_stats(user_id)
    return {"link": link, "stats": stats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
