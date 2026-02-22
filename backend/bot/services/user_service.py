import logging

from db.database import async_session
from db.models import User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def get_or_create_user(user_id: int, username: str):
    async with async_session() as session:
        try:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                new_user = User(id=user_id, username=username)
                session.add(new_user)
                await session.commit()
                logger.info(f"Создан новый пользователь: {user_id}")
            else:
                logger.debug(f"Пользователь уже существует: {user_id}")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении пользователя: {e}")