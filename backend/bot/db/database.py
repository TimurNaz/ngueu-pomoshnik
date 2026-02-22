from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Сессия для взаимодействия с БД
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Базовый класс моделей
Base = declarative_base()

# Dependency-like функция (как в FastAPI)
async def get_db():
    async with async_session() as session:
        yield session