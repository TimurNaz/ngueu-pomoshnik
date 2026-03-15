import os
import sys
import subprocess
from datetime import datetime
import logging
from pathlib import Path
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Пути
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
BOT_DIR = BACKEND_DIR / "bot"
ROOT_ENV = BASE_DIR / ".env"
BOT_ENV = BOT_DIR / ".env"
BACKUP_DIR = BASE_DIR / "backups"

# Путь к pg_dump v15 в macOS (через Homebrew)
PG_DUMP_V15 = "/opt/homebrew/opt/postgresql@15/bin/pg_dump"

# Загружаем .env (сначала из корня, потом из папки бота)
if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV)
    logger.info(f"✅ Загружен .env из корня: {ROOT_ENV}")
elif BOT_ENV.exists():
    load_dotenv(dotenv_path=BOT_ENV)
    logger.info(f"✅ Загружен .env из папки бота: {BOT_ENV}")
else:
    logger.error("❌ Файл .env не найден ни в корне, ни в папке бота")
    sys.exit(1)

# Получаем настройки БД
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    logger.error("❌ В .env отсутствуют необходимые переменные (DB_USER, DB_PASSWORD, DB_NAME)")
    sys.exit(1)

def create_backup():
    """Создает дамп базы данных PostgreSQL с помощью pg_dump."""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)
        logger.info(f"📁 Создана директория для бэкапов: {BACKUP_DIR}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"backup_{DB_NAME}_{timestamp}.sql"

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    # Пробуем использовать pg_dump v15, если он существует, иначе дефолтный
    pg_dump_cmd = PG_DUMP_V15 if os.path.exists(PG_DUMP_V15) else "pg_dump"

    command = [
        pg_dump_cmd,
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", DB_NAME,
        "-f", str(backup_file),
        "-v"
    ]

    try:
        logger.info(f"🚀 Запуск резервного копирования (используем {pg_dump_cmd}) базы '{DB_NAME}'...")
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        logger.info(f"✅ Бэкап успешно создан: {backup_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Ошибка при создании бэкапа: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"❌ Ошибка: Утилита '{pg_dump_cmd}' не найдена.")
        sys.exit(1)

if __name__ == "__main__":
    create_backup()
