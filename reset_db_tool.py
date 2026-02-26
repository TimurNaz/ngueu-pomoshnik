import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь для импортов
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend" / "bot"))

from db.database import engine
from db.models import Base

async def reset_db():
    print("⏳ Начинаю полную очистку базы данных (DROP SCHEMA public)...")
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            # Удаляем и создаем заново схему public. 
            # Это удалит ВСЕ таблицы и ENUM типы разом.
            await conn.execute(text("DROP SCHEMA public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public;")) 
            
        print("✅ База данных полностью очищена.")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(reset_db())
