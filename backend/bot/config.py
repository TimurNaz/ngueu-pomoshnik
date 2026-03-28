import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _require_env(name: str) -> str:
    """Возвращает значение переменной окружения или завершает процесс."""
    value = os.getenv(name)
    if not value:
        logger.critical(f"Переменная окружения {name} не задана! Проверьте .env файл.")
        sys.exit(1)
    return value


# ── Telegram Bot ──────────────────────────────────────────────
TOKEN: str = _require_env("BOT_TOKEN")

# Список ID администраторов (через запятую в .env)
_admin_ids_raw = os.getenv("ADMIN_IDS", "")
# Очищаем от кавычек и пробелов, прежде чем разбивать по запятой
_admin_ids_clean = _admin_ids_raw.replace("'", "").replace('"', "").strip()
ADMIN_IDS: list[int] = [int(i.strip()) for i in _admin_ids_clean.split(",") if i.strip().isdigit()]

# ── PostgreSQL ────────────────────────────────────────────────
DB_USER: str = _require_env("DB_USER")
DB_PASSWORD: str = _require_env("DB_PASSWORD")
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str = _require_env("DB_NAME")

DATABASE_URL: str = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Redis ─────────────────────────────────────────────────────
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── MiniApp (frontend) ────────────────────────────────────────
# URL главной страницы MiniApp. Должен быть HTTPS.
MINIAPP_URL: str = os.getenv("MINIAPP_URL", "https://olddiamond.online")

# ── Payments ─────────────────────────────────────────────
PAYMENT_PROVIDER: str = os.getenv("PAYMENT_PROVIDER", "mock")
PAYMENT_SHOP_ID: str = os.getenv("PAYMENT_SHOP_ID", "")
PAYMENT_SECRET_KEY: str = os.getenv("PAYMENT_SECRET_KEY", "")
PAYMENT_RETURN_URL: str = os.getenv("PAYMENT_RETURN_URL", f"{MINIAPP_URL}/orders")
PAYMENT_WEBHOOK_SECRET: str = os.getenv("PAYMENT_WEBHOOK_SECRET", "")