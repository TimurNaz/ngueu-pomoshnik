import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь для импортов модулей бота и базы данных
# Скрипт лежит в backend/utils/scripts/, поэтому нам нужно подняться на 3 уровня вверх
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "backend" / "bot"))

from db.database import engine
from db.models import Base

async def reset_db():
    """
    ВНИМАНИЕ: Этот скрипт полностью удаляет структуру базы данных (таблицы и типы)!
    Используйте только в среде разработки.
    """
    print("⏳ Начинаю полную очистку базы данных (DROP SCHEMA public)...")
    confirm = input("⚠️ Вы уверены, что хотите УДАЛИТЬ все данные? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Очистка отменена.")
        return

    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            # Удаляем и создаем заново схему public. 
            # Это удалит ВСЕ таблицы и ENUM типы разом.
            await conn.execute(text("DROP SCHEMA public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public;")) 
            
        print("✅ База данных полностью очищена. Теперь выполните: alembic upgrade head")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(reset_db())
