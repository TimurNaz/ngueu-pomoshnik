import hmac
import hashlib
import os
import logging
from urllib.parse import parse_qsl
from fastapi import Request, HTTPException, Depends

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

def verify_telegram_webapp_data(init_data: str) -> bool:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в переменных окружения")
        return False
        
    try:
        vals = dict(parse_qsl(init_data))
        hash_str = vals.pop('hash', None)
        if not hash_str: return False

        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return calculated_hash == hash_str
    except Exception as e:
        logger.error(f"Ошибка при валидации initData: {e}")
        return False

async def check_tg_auth(request: Request):
    # Пропускаем проверку для технических путей
    if request.url.path in ["/api/health", "/docs", "/openapi.json", "/favicon.ico"] or request.url.path.startswith("/static"):
        return

    init_data = request.headers.get("X-TG-Init-Data")
    
    # ЕСЛИ МЫ В РЕЖИМЕ ОТЛАДКИ — пропускаем без init_data
    if DEBUG_MODE and (not init_data or init_data == "undefined" or init_data == ""):
        logger.info(f"DEBUG_MODE: Пропуск авторизации для {request.url.path}")
        return

    if not init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram Init Data")
        
    if not verify_telegram_webapp_data(init_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram Init Data")
