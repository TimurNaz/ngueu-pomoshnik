import sys
import os
import asyncio
import logging

# Добавляем корень бота в PYTHONPATH до остальных импортов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.database import engine
from db.models import Base

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Таблицы успешно созданы.")


if __name__ == "__main__":
    asyncio.run(init_models())