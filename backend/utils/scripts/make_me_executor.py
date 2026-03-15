
import asyncio
import sys
import os
from pathlib import Path

# Определяем корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Добавляем пути, чтобы Python видел модули
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "backend" / "bot"))

# Теперь пробуем импортить
try:
    from db.database import async_session
    from db.models import User, UserRole, ExecutorProfile
    from sqlalchemy import select
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Попробуй запустить: pip install sqlalchemy asyncpg")
    sys.exit(1)

async def fix_user():
    my_id = 8360967543
    async with async_session() as session:
        user = await session.get(User, my_id)
        if not user:
            print(f"❌ Пользователь {my_id} не найден в базе. Сначала нажми /start в боте!")
            return
            
        user.role = UserRole.executor
        user.is_active = True
        
        res = await session.execute(select(ExecutorProfile).where(ExecutorProfile.user_id == my_id))
        profile = res.scalar_one_or_none()
        
        if not profile:
            profile = ExecutorProfile(
                user_id=my_id, 
                is_verified=True, 
                is_available=True, 
                rating=5.0, 
                specializations=["Тест"], 
                bio="Админ"
            )
            session.add(profile)
        else:
            profile.is_verified = True
            profile.is_available = True
            
        await session.commit()
        print(f"✅ Успешно! Пользователь {user.username or my_id} теперь исполнитель.")

if __name__ == "__main__":
    asyncio.run(fix_user())
