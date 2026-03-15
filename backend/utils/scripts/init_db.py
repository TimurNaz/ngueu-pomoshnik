import os
import sys
import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Пути
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
BOT_DIR = BACKEND_DIR / "bot"

# Добавляем пути в sys.path для корректных импортов
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BOT_DIR))

# Импортируем после настройки путей
try:
    from bot.db.database import engine
    from bot.db.models import Base
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

async def init_models():
    """Создает все таблицы, определенные в моделях."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Таблицы успешно созданы в базе данных.")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации БД: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(init_models())
