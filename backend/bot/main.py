import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import TOKEN
from handlers import common, client, executor, admin

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        bot = Bot(
            token=TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )

        # TODO: В production заменить на RedisStorage для сохранения FSM-состояний
        # from aiogram.fsm.storage.redis import RedisStorage
        # from config import REDIS_URL
        # storage = RedisStorage.from_url(REDIS_URL)
        storage = MemoryStorage()

        dp = Dispatcher(storage=storage)

        # Подключаем все роутеры
        dp.include_router(common.router)
        dp.include_router(client.router)
        dp.include_router(executor.router)
        dp.include_router(admin.router)

        logger.info("Бот запущен.")
        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())