import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Настройка путей для импорта
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
sys.path.append(str(BACKEND_DIR))
sys.path.append(str(BACKEND_DIR / "bot"))

from api.auth import check_tg_auth
from api.routers import users, orders, system, notifications, payments
from api.utils.logging import StructuredLoggingMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NGUEU Helper API", 
    version="2.0.2",
    dependencies=[Depends(check_tg_auth)]
)

# Подключаем структурированное логирование
app.add_middleware(StructuredLoggingMiddleware)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статику (загруженные файлы)
UPLOAD_DIR = Path("backend/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Подключаем роутеры с глобальным префиксом /api (для совместимости с Nginx)
app.include_router(system.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(payments.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
