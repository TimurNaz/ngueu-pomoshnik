import os
import sys
import asyncio
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Пути
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent
BOT_DIR = BACKEND_DIR / "bot"

# Добавляем пути в sys.path
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BOT_DIR))

try:
    from bot.db.database import async_session
    from bot.db.models import User, Order, UserRole, WorkType, UrgencyLevel, OrderStatus, ExecutorProfile
    from sqlalchemy import select
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

# Тестовые данные
SUBJECTS = ["Математика", "Экономика", "Информатика", "История", "Право", "Маркетинг"]
TOPICS = ["Анализ деятельности", "Цифровая трансформация", "Разработка системы", "Исследование рынка", "Налоги"]
NAMES = ["Александр", "Мария", "Дмитрий", "Елена", "Сергей", "Анна", "Игорь", "Ольга"]
SURNAMES = ["Иванов", "Петрова", "Сидоров", "Кузнецова", "Васильев", "Попова"]

async def create_test_data():
    """Генерирует тестовых пользователей (клиентов и исполнителей) и заказы."""
    async with async_session() as session:
        logger.info("🚀 Запуск генерации тестовых данных...")

        # 1. Создаем тестовых КЛИЕНТОВ
        test_clients = []
        for i in range(3):
            user_id = 1000000 + i
            # Проверяем существование
            user = await session.get(User, user_id)
            if not user:
                user = User(
                    id=user_id,
                    username=f"client_{i}",
                    first_name=random.choice(NAMES),
                    last_name=random.choice(SURNAMES),
                    role=UserRole.client,
                    referral_code=f"REF{user_id}"
                )
                session.add(user)
                logger.info(f"👤 Добавлен клиент: {user.username}")
            test_clients.append(user)

        # 2. Создаем тестовых ИСПОЛНИТЕЛЕЙ
        test_executors = []
        for i in range(3):
            user_id = 2000000 + i
            user = await session.get(User, user_id)
            if not user:
                user = User(
                    id=user_id,
                    username=f"executor_{i}",
                    first_name=random.choice(NAMES),
                    last_name=random.choice(SURNAMES),
                    role=UserRole.executor,
                    is_active=True
                )
                session.add(user)
                await session.flush()

                profile = ExecutorProfile(
                    user_id=user.id,
                    specializations=["Математика", "Экономика"],
                    bio="Опытный исполнитель.",
                    experience_years=random.randint(1, 5),
                    rating=round(random.uniform(4.5, 5.0), 1),
                    is_verified=True,
                    is_available=True
                )
                session.add(profile)
                logger.info(f"🛠 Добавлен исполнитель: {user.username} (Рейтинг: {profile.rating})")
            test_executors.append(user)

        await session.commit()

        # 3. Создаем тестовые заказы (только если их мало)
        result = await session.execute(select(Order))
        if len(result.scalars().all()) < 5:
            for i in range(5):
                client = random.choice(test_clients)
                order = Order(
                    client_id=client.id,
                    work_type=random.choice(list(WorkType)),
                    subject=random.choice(SUBJECTS),
                    topic=f"{random.choice(TOPICS)} №{random.randint(100, 999)}",
                    deadline=datetime.now() + timedelta(days=random.randint(7, 30)),
                    urgency=random.choice(list(UrgencyLevel)),
                    status=OrderStatus.new,
                    price=random.randint(1500, 10000)
                )
                session.add(order)
                logger.info(f"📦 Добавлен заказ: {order.topic}")

        await session.commit()
        logger.info("✅ База данных актуализирована.")

if __name__ == "__main__":
    asyncio.run(create_test_data())
