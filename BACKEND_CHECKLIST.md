# BACKEND CHECKLIST — НГУЭУ Помощник

> Обновлено: 27 февраля 2026 г.

---

## 1. Конфигурация и окружение

| Элемент | Статус | Комментарий |
|---------|--------|-------------|
| `.env` файл | ✅ Готово | `BOT_TOKEN`, `DB_*`, `MINIAPP_URL` настроены |
| `config.py` — валидация переменных | ✅ Готово | `_require_env()`, `sys.exit(1)` при отсутствии |
| `config.py` — `MINIAPP_URL` | ✅ Готово | Поддержка ngrok URL |
| `requirements.txt` | ✅ Готово | aiogram 3.25, SQLAlchemy, FastAPI, Alembic и др. |
| `.gitignore` | ✅ Готово | Все основные паттерны |
| `.vscode/settings.json` | ✅ Готово | Интерпретатор `.venv`, extraPaths |
| `pyrightconfig.json` | ✅ Готово | Для Pylance |

---

## 2. База данных — Модели (`db/models.py`)

| Модель | Статус | Строк | Связи |
|--------|--------|-------|-------|
| `User` | ✅ Готово | ~45 | role, loyalty, бонусы, referral, timestamps |
| `ExecutorProfile` | ✅ Готово | ~25 | 1:1 с User, специализации, рейтинг |
| `Order` | ✅ Готово | ~45 | client → User, executor → User, финансы, прогресс |
| `Payment` | ✅ Готово | ~25 | order → Order, user → User, YooKassa ID |
| `BonusTransaction` | ✅ Готово | ~20 | user → User, order → Order |
| `Referral` | ✅ Готово | ~20 | referrer → User, referred → User |
| `Review` | ✅ Готово | ~20 | order → Order, NPS score |
| `HolidayBonus` | ✅ Готово | ~15 | target levels, trigger date |
| `KnowledgeBase` | ✅ Готово | ~20 | teacher, dept, author → User |

**Enums**: `UserRole`, `LoyaltyLevel`, `OrderStatus`, `PaymentStatus`, `PaymentStage`, `BonusType`, `ReferralStatus`, `HolidayTarget`, `WorkType`, `UrgencyLevel` — все 10 определены.

**Бизнес-константы**: `LOYALTY_THRESHOLDS`, `CASHBACK_RATES`, `REGISTRATION_BONUS` (500₽), `REFERRAL_BONUS` (100₽), `COMMISSION_RATE` (10%), `MAX_BONUS_RATIO` (50%).

---

## 3. База данных — Инфраструктура

| Элемент | Статус | Комментарий |
|---------|--------|-------------|
| `database.py` — движок, сессия, Base | ✅ Готово | `asyncpg`, `AsyncSession` |
| `init_db.py` — создание таблиц | ✅ Готово | `Base.metadata.create_all` |
| `alembic.ini` | ✅ Готово | `script_location = backend/migrations` |
| `backend/migrations/env.py` | ✅ Готово | Async-миграции, `.env` загрузка |
| `backend/migrations/versions/001_initial.py` | ✅ Готово | 311 строк, все 9 таблиц + 10 ENUM + индексы |
| `db/redis.py` | ⚠️ Заглушка | Весь код закомментирован |

---

## 4. Сервисный слой (`services/`)

| Сервис | Статус | Файл | Методы |
|--------|--------|------|--------|
| `UserService` | ✅ Готово | `db_service.py` | `get_or_create`, `get_by_id`, `get_by_referral_code`, `update_loyalty`, `get_referral_link`, `get_referral_stats` |
| `BonusService` | ✅ Готово | `db_service.py` | `add`, `spend`, `apply_cashback`, `get_history` |
| `ReferralService` | ✅ Готово | `db_service.py` | `activate_if_first_purchase` |
| `OrderService` | ✅ Готово | `db_service.py` | `create`, `assign_executor`, `start_work`, `send_for_review`, `complete`, `cancel`, `get_client_orders`, `get_by_id` |
| `HolidayService` | ✅ Готово | `db_service.py` | `create`, `send_pending` |
| `ReviewService` | ✅ Готово | `db_service.py` | `create`, `get_published` |
| Обратная совместимость | ✅ Готово | `user_service.py` | Обёртка для старых handlers |

---

## 5. Бот — Хендлеры (`handlers/`)

| Хендлер | Статус | Функционал |
|---------|--------|------------|
| `common.py` | ✅ Готово | `/start`, согласие, go_back |
| `client.py` | ✅ Готово | Меню: ЛК, О нас, Этапы, FAQ (9 тем), Отзывы, Поддержка, Стать исполнителем |
| `executor.py` | ⚠️ Заглушка | Только стаб «В разработке» |
| `admin.py` | ⚠️ Заглушка | Только стаб «В разработке» |

---

## 6. Бот — Клавиатуры (`keyboards/`)

| Элемент | Статус | Комментарий |
|---------|--------|-------------|
| `client.py` — основные клавиатуры | ✅ Готово | Consent, Start, FAQ, Back, About |
| `client.py` — MiniApp кнопка | ✅ Готово | `WebAppInfo` + `_miniapp_url()` |
| `faq_data.py` — данные FAQ | ✅ Готово | 9 категорий вопросов |
| Картинки в Yandex Cloud | ✅ Готово | Все URL актуальны |

---

## 7. Frontend (MiniApp)

| Элемент | Статус | Комментарий |
|---------|--------|-------------|
| Vite + React | ✅ Готово | `frontend/` с `vite.config.js` |
| Компоненты (`src/components/`) | ✅ Готово | 8 компонентов |
| Страницы (`src/pages/`) | ✅ Готово | 7 страниц |
| Стили (`src/styles/`) | ✅ Готово | 17 CSS-файлов |
| `CLAUDE.md` | ✅ Есть | Инструкции для AI |
| Деплой | ⚠️ Через ngrok | Нет постоянного хостинга |

---

## 8. Инфраструктура

| Элемент | Статус | Комментарий |
|---------|--------|-------------|
| `Dockerfile` | ❌ Пустой | Нужно написать |
| `docker-compose.yml` | ❌ Пустой | Нужно написать |
| `README.md` | ❌ Пустой | Нужно написать документацию |
| CI/CD | ❌ Нет | Нет GitHub Actions / pipeline |

---

## 9. Пустые директории (заготовки)

| Директория | Назначение | Статус |
|-----------|------------|--------|
| `backend/api/` | FastAPI REST API | ❌ Пустая |
| `backend/ai_assistant/` | AI-помощник | ❌ Пустая |
| `backend/models/` | Pydantic-схемы для API | ❌ Пустая |
| `backend/utils/` | Общие утилиты | ❌ Пустая |
| `backend/tests/` | Тесты | ❌ Пустая |
| `db_layer/` | Неизвестно (только .DS_Store) | ❌ Можно удалить |

---

## 10. Найденные баги и проблемы

| # | Проблема | Критичность | Файл |
|---|---------|-------------|------|
| 1 | **Дубль `migrations/`** — существует и `backend/migrations/` и корневой `migrations/`. `alembic.ini` ссылается на `backend/migrations`. Корневой `migrations/` — лишний | 🟡 Средняя | `/migrations/` |
| 2 | **Placeholder URLs** — `instagram.com/yourpage` и `t.me/your_feedback_channel` в `keyboards/client.py` | 🟡 Средняя | `keyboards/client.py:129-130` |
| 3 | **Executor/Admin картинки** — `imgur.com` ссылки в хендлерах (остальные на Yandex Cloud) | 🟢 Низкая | `executor.py:10`, `admin.py:10` |
| 4 | **`env.py` содержит `EOF`** — последняя строка файла содержит текст `EOF` | 🟡 Средняя | `backend/migrations/env.py:74` |
| 5 | **`redis.py` полностью закомментирован** — весь файл-заглушка | 🟢 Низкая | `db/redis.py` |
| 6 | **`WorkType` определён дважды** — и в `models.py` (строка 220) и в Enum в `001_initial.py` — потенциальная рассинхронизация при изменении | 🟢 Информация | — |
| 7 | **Нет модели `notifications`** — упоминается в FAQ/функционале, но модели нет | 🟢 Информация | — |

---

## 11. Рекомендуемые следующие шаги (приоритет)

### Высокий приоритет
1. **Реализовать хендлеры исполнителя** — подключить `OrderService` к `executor.py`
2. **Реализовать хендлеры админа** — назначение исполнителей, управление заявками
3. **Интегрировать YooKassa** — `PaymentService` в `db_service.py`, webhook
4. **Перенести MiniApp-форму заявки** — подключить frontend к `OrderService.create()`

### Средний приоритет
5. **Подключить Redis** — раскомментировать `redis.py`, FSM storage, кеширование FAQ
6. **Написать FastAPI REST API** (`backend/api/`) — для MiniApp, для внешних интеграций
7. **Dockerfile + docker-compose** — PostgreSQL, Redis, бот, frontend
8. **Удалить дубли** — корневой `migrations/`, `db_layer/`

### Низкий приоритет
9. **Написать тесты** — unit-тесты для `db_service.py`
10. **README.md** — инструкция по развёртыванию
11. **CI/CD** — GitHub Actions для линтинга и тестов
12. **Заменить imgur-картинки** на Yandex Cloud (executor/admin)
13. **Заменить placeholder URLs** (Instagram, Telegram-канал отзывов)

---

## Общая статистика

| Метрика | Значение |
|---------|----------|
| Python-файлов (backend) | 25 |
| Строк кода (models.py) | 437 |
| Строк кода (db_service.py) | 686 |
| Строк кода (миграция) | 311 |
| Таблиц в БД | 9 |
| Enum-типов | 10 |
| Frontend-компонентов | 8 |
| Frontend-страниц | 7 |
| Хендлеров бота | 4 (2 активных, 2 стаба) |
| Сервисов | 6 |
| Тестов | 0 |
