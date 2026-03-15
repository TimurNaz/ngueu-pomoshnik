import logging
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from api.schemas.user import UserProfile
from api.auth import DEBUG_MODE
from db.database import async_session
from services.db_service import UserService, BonusService
from db.models import User, BonusType

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int):
    logger.info(f"--- PROFILE REQUEST: user_id={user_id} ---")
    user = await UserService.get_by_id(user_id)
    
    if not user:
        logger.warning(f"User {user_id} NOT FOUND in DB. Creating new one...")
        user, is_new = await UserService.get_or_create(telegram_id=user_id, username=f"user_{user_id}")
        logger.info(f"New user created: {user_id}, is_new={is_new}")
    
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "bonus_balance": float(user.bonus_balance),
        "loyalty_level": user.loyalty_level.value if hasattr(user.loyalty_level, 'value') else str(user.loyalty_level),
        "total_spent": float(user.total_spent)
    }

@router.get("/{user_id}/bonuses")
async def get_user_bonus_history(user_id: int):
    return await BonusService.get_history(user_id)

@router.get("/{user_id}/referral")
async def get_user_referral(user_id: int):
    bot_username = "NGU_StudBot" 
    link = await UserService.get_referral_link(user_id, bot_username)
    stats = await UserService.get_referral_stats(user_id)
    return {"link": link, "stats": stats}

@router.post("/debug/bonus/{user_id}")
async def debug_add_bonus(user_id: int):
    if not DEBUG_MODE:
        raise HTTPException(status_code=403, detail="Debug mode disabled")
    
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user, _ = await UserService.get_or_create(telegram_id=user_id, username=f"debug_{user_id}")
            user = await session.get(User, user_id)
            
        await BonusService.add(session, user, Decimal("500"), BonusType.registration, "Ручное начисление (Debug)")
        await session.commit()
        return {"status": "success", "new_balance": float(user.bonus_balance)}
