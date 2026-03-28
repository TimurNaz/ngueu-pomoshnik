import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("api")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8] # Используем короткий ID для читаемости
        start_time = time.time()
        
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Пытаемся определить имя обработчика (функции)
        # В FastAPI это можно сделать через scope
        handler_name = "router"
        if "route" in request.scope:
            handler_name = request.scope["route"].name
        elif "endpoint" in request.scope:
            handler_name = request.scope["endpoint"].__name__

        # Логируем начало запроса
        logger.info(f"🚀 START | {request_id} | {handler_name: <20} | {method} {path}")
        
        try:
            response = await call_next(request)
            
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = "{0:.2f}ms".format(process_time)
            
            # Логируем завершение запроса
            logger.info(
                f"✅ END   | {request_id} | {formatted_process_time: >8} | Status: {response.status_code}"
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"❌ ERROR | {request_id} | {path} | {str(e)}", 
                exc_info=True
            )
            raise
