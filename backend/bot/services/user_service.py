"""
backend/bot/services/user_service.py
=====================================
Обратная совместимость + новые методы.
Старый get_or_create_user() сохранён — бот не сломается.
"""
import logging
from typing import Optional

from db.database import async_session
from db.models import User
from services.db_service import UserService as _US, BonusService, OrderService

logger = logging.getLogger(__name__)


# ── Старый интерфейс (используется в handlers/common.py) ────────

async def get_or_create_user(user_id: int, username: str) -> User:
    """
    Совместимая обёртка для существующих handlers.
    Внутри вызывает новый UserService.
    """
    user, is_new = await _US.get_or_create(
        telegram_id=user_id,
        username=username,
    )
    if is_new:
        logger.info(f"Новый пользователь зарегистрирован: {user_id}, бонус +500₽")
    return user


# ── Новые методы для новых handlers ─────────────────────────────

async def get_user(telegram_id: int) -> Optional[User]:
    return await _US.get_by_id(telegram_id)


async def get_referral_link(telegram_id: int, bot_username: str) -> str:
    return await _US.get_referral_link(telegram_id, bot_username)


async def get_referral_stats(telegram_id: int) -> dict:
    return await _US.get_referral_stats(telegram_id)


async def get_bonus_history(telegram_id: int, limit: int = 10):
    return await BonusService.get_history(telegram_id, limit)
