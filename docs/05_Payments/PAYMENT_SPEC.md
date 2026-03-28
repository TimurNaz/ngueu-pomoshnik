# Интеграция оплаты — ФТТ и ТЗ

> Версия: 2.0 | Дата: 2026-03-22
> Статус: **Этапы 1–3 реализованы, Этап 4 — подключение провайдера**

---

## 1. Общее описание

Подключение онлайн-оплаты заказов через платёжный провайдер (YooKassa или аналог) внутри Telegram Mini App. Оплата происходит на карточке заказа в разделе "Мои заявки".

### 1.1 Цели

- Клиент может оплатить заказ онлайн после назначения цены исполнителем
- Система автоматически обрабатывает статусы платежа через webhooks
- Защита клиента: возврат в течение 1 часа, заморозка 50% до подтверждения
- Защита платформы: автоотмена неоплаченных заказов, арбитраж через админа

### 1.2 Ограничения текущего этапа

- Платёжный провайдер ещё не выбран окончательно → абстрактный интерфейс провайдера
- Разработка и тестирование на `MockProvider`
- Выплаты исполнителям — вручную через админа (без электронного кошелька)

---

## 2. Бизнес-процесс оплаты (полный flow)

### 2.1 Диаграмма статусов заказа

```
new → assigned → priced → paid → in_progress → review → done → confirming → completed
  │                │        │                                        │
  └── canceled ◄───┘        │                                        ├── completed (авто через 2 дня)
                            │                                        └── disputed → completed / refunded_partial
                            │
                            └── canceled (авто через 48ч без оплаты)
```

### 2.2 Пошаговый flow

| # | Действие | Актор | Статус заказа | Платёж | Уведомления |
|---|----------|-------|---------------|--------|-------------|
| 1 | Создаёт заявку | Клиент (Mini App) | `new` | — | Push админам в TG |
| 2 | Назначает исполнителя | Админ (TG бот) | `assigned` | — | Push клиенту + in-app |
| 3 | Устанавливает цену | Исполнитель (TG бот) | `priced` | — | Push клиенту: "Цена назначена: X ₽" + in-app |
| 4 | Открывает заказ, видит блок оплаты | Клиент (Mini App) | `priced` | — | — |
| 5 | Выбирает бонусы к списанию, жмёт "Оплатить" | Клиент (Mini App) | `priced` | `pending` → redirect на провайдера | — |
| 6 | Оплачивает на стороне провайдера | Клиент | `priced` | `waiting` | — |
| 7 | Webhook от провайдера: оплата успешна | Система | `paid` | `paid` | Push клиенту + админу + in-app |
| 8 | **1 час на отмену** — клиент может отменить | Клиент (Mini App) | `paid` → `canceled` | `refunded` (100%) | Push всем + in-app |
| 9 | Начинает работу (после 1 часа) | Исполнитель (TG бот) | `in_progress` | — | Push клиенту + in-app |
| 10 | Сдаёт работу | Исполнитель (TG бот) | `review` | — | Push клиенту + админу |
| 11 | Проверяет и одобряет, отправляет клиенту | Админ (TG бот) | `done` | 50% разморожено → исполнителю | Push клиенту: "Работа готова!" |
| 12 | **2 дня на проверку клиентом** | Клиент (Mini App) | `confirming` | 50% заморожено | Напоминание через 24ч |
| 13а | Подтверждает: "Всё ок" | Клиент (Mini App) | `completed` | Замороженные 50% → исполнителю | Push исполнителю |
| 13б | Молчит 2 дня | Система (авто) | `completed` | Замороженные 50% → исполнителю (авто) | Push клиенту + исполнителю |
| 13в | "Не принята преподом" | Клиент (Mini App) | `disputed` | Ждёт решения админа | Push админу |
| 14 | Арбитраж | Админ (TG бот) | `completed` или частичный возврат | Возврат 50% клиенту ИЛИ перевод исполнителю | Push обоим |

### 2.3 Автоматические действия (фоновые задачи)

| Триггер | Действие | Таймаут |
|---------|----------|---------|
| Заказ в статусе `priced`, нет оплаты | Напоминание push + in-app | 12ч, 24ч, 36ч |
| Заказ в статусе `priced`, нет оплаты | Автоотмена заказа | 48ч |
| Заказ в статусе `paid`, прошёл 1 час | Убрать возможность отмены | 1ч |
| Заказ в статусе `confirming`, нет ответа | Автоподтверждение | 48ч (2 дня) |
| Заказ в статусе `confirming` | Напоминание клиенту | 12ч, 24ч, 36ч |

---

## 3. Финансовая модель

### 3.1 Распределение суммы

```
Цена заказа (order.price)     = 10 000 ₽
  - Бонусы клиента (bonus_used)  =  2 000 ₽  (макс 50% от цены)
  ─────────────────────────────────────────
  Сумма к оплате через провайдера = 8 000 ₽  (payment.amount)

  Комиссия платформы (10%)        = 1 000 ₽  (commission_amount, от полной цены)
  Исполнителю                     = 9 000 ₽  (executor_amount = price - commission)
```

### 3.2 Заморозка и разморозка

Технически: вся сумма **захватывается сразу** (не холд провайдера). "Заморозка" — внутренняя логика в БД.

| Момент | Действие | frozen_amount | released_amount |
|--------|----------|---------------|-----------------|
| Оплата прошла | 50% замораживается | 50% от payment.amount | 0 |
| Админ одобрил (status: done) | 50% размораживается | 50% | 50% |
| Клиент подтвердил / авто 2 дня | Остаток размораживается | 0 | 100% |
| Клиент оспорил → админ решил возврат | Refund 50% через API провайдера | 0 | 50% + refund |

### 3.3 Возвраты

| Сценарий | Сумма возврата | Способ | Кто инициирует |
|----------|----------------|--------|----------------|
| Отмена в первый час после оплаты | 100% от payment.amount | Refund API провайдера | Клиент (кнопка) |
| Работа не принята преподом (disputed) | 50% от payment.amount (замороженная часть) | Refund API провайдера | Админ (после арбитража) |
| Провайдер не подтвердил оплату | 0 (деньги не списались) | — | Автоматически |

**Важно**: комиссия провайдера (~3.5%) при возврате не возвращается мерчанту. Каждый refund — убыток платформы.

### 3.4 Выплаты исполнителям (v1 — ручной режим)

- `executor_amount` фиксируется в системе при установке цены
- В интерфейсе админа (TG бот): команда для просмотра задолженностей
- Админ переводит деньги вручную (карта/СБП)
- В БД отмечается факт выплаты (поле `executor_paid` в Payment)

---

## 4. Изменения в БД (миграция 003)

### 4.1 Новые значения Enum

```python
# OrderStatus — добавить:
class OrderStatus(str, enum.Enum):
    new         = "new"
    assigned    = "assigned"
    priced      = "priced"        # НОВЫЙ: цена назначена, ждём оплаты
    paid        = "paid"          # НОВЫЙ: оплачен
    in_progress = "in_progress"
    review      = "review"
    done        = "done"
    confirming  = "confirming"    # НОВЫЙ: клиент проверяет работу (2 дня)
    completed   = "completed"     # НОВЫЙ: финально завершён
    disputed    = "disputed"      # НОВЫЙ: клиент оспаривает
    canceled    = "canceled"

# NotificationType — добавить:
class NotificationType(str, enum.Enum):
    ...
    price_set          = "price_set"           # НОВЫЙ
    payment_pending    = "payment_pending"     # НОВЫЙ
    payment_success    = "payment_success"     # НОВЫЙ
    payment_refunded   = "payment_refunded"    # НОВЫЙ
    order_confirming   = "order_confirming"    # НОВЫЙ
    order_completed    = "order_completed"     # НОВЫЙ
    order_disputed     = "order_disputed"      # НОВЫЙ
    payment_reminder   = "payment_reminder"    # НОВЫЙ
```

### 4.2 Изменения модели Payment

```python
class Payment(Base):
    __tablename__ = "payments"
    id                   = Column(Integer, primary_key=True)
    order_id             = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id              = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount               = Column(Numeric(12, 2), nullable=False)          # Сумма к оплате (после вычета бонусов)
    status               = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    stage                = Column(Enum(PaymentStage), nullable=False)
    provider_payment_id  = Column(String(64), unique=True, nullable=True)  # Переименовать yookassa_payment_id
    provider_name        = Column(String(32), nullable=True)               # НОВОЕ: "yookassa" / "mock" / etc.
    frozen_amount        = Column(Numeric(12, 2), nullable=True)           # НОВОЕ: замороженная часть (50%)
    released_amount      = Column(Numeric(12, 2), default=0)              # НОВОЕ: размороженная часть
    refunded_amount      = Column(Numeric(12, 2), default=0)              # НОВОЕ: возвращённая сумма
    bonus_used           = Column(Numeric(12, 2), default=0)              # НОВОЕ: бонусы, использованные в этом платеже
    executor_paid        = Column(Boolean, default=False)                  # НОВОЕ: админ выплатил исполнителю
    executor_paid_at     = Column(DateTime(timezone=True), nullable=True)  # НОВОЕ
    cancel_deadline      = Column(DateTime(timezone=True), nullable=True)  # НОВОЕ: до когда можно отменить (created_at + 1ч)
    confirmation_deadline = Column(DateTime(timezone=True), nullable=True) # НОВОЕ: дедлайн подтверждения клиентом
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    paid_at              = Column(DateTime(timezone=True), nullable=True)
    # ... relationships
```

### 4.3 Изменения модели Order

```python
class Order(Base):
    # Существующие поля остаются
    ...
    priced_at     = Column(DateTime(timezone=True), nullable=True)   # НОВОЕ: когда назначена цена
    paid_at       = Column(DateTime(timezone=True), nullable=True)   # НОВОЕ: когда оплачен
    confirmed_at  = Column(DateTime(timezone=True), nullable=True)   # НОВОЕ: когда клиент подтвердил
    payment_deadline = Column(DateTime(timezone=True), nullable=True) # НОВОЕ: дедлайн оплаты (priced_at + 48ч)
```

---

## 5. Backend — новые компоненты

### 5.1 Абстракция платёжного провайдера

**Файл**: `backend/bot/services/payment_provider.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class PaymentResult:
    provider_payment_id: str
    confirmation_url: str      # URL для редиректа клиента
    status: str

@dataclass
class RefundResult:
    provider_refund_id: str
    status: str
    amount: Decimal

class PaymentProvider(ABC):
    @abstractmethod
    async def create_payment(
        self,
        amount: Decimal,
        description: str,
        order_id: int,
        return_url: str,
    ) -> PaymentResult: ...

    @abstractmethod
    async def refund(
        self,
        provider_payment_id: str,
        amount: Decimal,
    ) -> RefundResult: ...

    @abstractmethod
    async def get_status(
        self,
        provider_payment_id: str,
    ) -> str: ...
```

**Реализации**:
- `MockProvider` — для разработки/тестов (сразу возвращает `paid`)
- `YooKassaProvider` — подключается позже

### 5.2 PaymentService

**Файл**: `backend/bot/services/payment_service.py`

```python
class PaymentService:
    """Бизнес-логика платежей."""

    async def initiate_payment(order_id, user_id, bonus_amount) -> dict:
        """
        1. Валидирует: заказ в статусе priced, цена назначена
        2. Рассчитывает: amount = price - bonus_used
        3. Списывает бонусы через BonusService.spend()
        4. Создаёт Payment в БД (status=pending)
        5. Вызывает provider.create_payment()
        6. Возвращает {payment_id, confirmation_url}
        """

    async def handle_webhook(provider_payment_id, status) -> None:
        """
        1. Находит Payment по provider_payment_id
        2. Обновляет Payment.status
        3. Если paid:
           - Order.status = paid
           - frozen_amount = 50% от amount
           - cancel_deadline = now + 1 час
           - Начисляет cashback
           - Отправляет уведомления
        4. Если failed:
           - Возвращает бонусы
           - Уведомляет клиента
        """

    async def cancel_payment(payment_id, user_id) -> bool:
        """
        1. Проверяет: cancel_deadline не прошёл
        2. Вызывает provider.refund(100%)
        3. Payment.status = refunded
        4. Order.status = canceled
        5. Возвращает бонусы
        6. Уведомляет всех
        """

    async def release_frozen(payment_id) -> None:
        """Размораживает 50% — вызывается при подтверждении клиентом или авто."""

    async def partial_refund(payment_id) -> None:
        """Возврат замороженных 50% — вызывается админом при disputed."""
```

### 5.3 SchedulerService (фоновые задачи)

**Файл**: `backend/bot/services/scheduler_service.py`

```python
class SchedulerService:
    """Фоновые задачи по расписанию."""

    async def check_payment_deadlines():
        """Каждые 30 мин: ищет priced-заказы старше 48ч → автоотмена."""

    async def send_payment_reminders():
        """Каждые 30 мин: push-напоминания через 12ч, 24ч, 36ч."""

    async def check_cancel_deadlines():
        """Каждые 5 мин: priced заказы, у которых прошёл cancel_deadline → убрать кнопку."""

    async def check_confirmation_deadlines():
        """Каждые 30 мин: confirming заказы старше 2 дней → автоподтверждение."""
```

Запуск: через `aiogram` startup hook или `apscheduler`.

### 5.4 API роутер `/payments`

**Файл**: `backend/api/routers/payments.py`

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/payments/create` | Инициировать оплату (order_id, bonus_amount) → {confirmation_url} |
| POST | `/api/payments/webhook` | Webhook от провайдера (без авторизации TG!) |
| POST | `/api/payments/{id}/cancel` | Отмена в течение 1 часа |
| GET | `/api/payments/order/{order_id}` | Получить платежи по заказу |
| POST | `/api/orders/{id}/confirm` | Клиент подтверждает работу |
| POST | `/api/orders/{id}/dispute` | Клиент оспаривает работу |

**Важно**: webhook-эндпоинт должен быть **исключён из TG-авторизации** (отдельный роутер без `check_tg_auth`).

### 5.5 Команды бота (TG)

| Команда / callback | Актор | Действие |
|-------------------|-------|----------|
| `set_price_{order_id}` | Исполнитель | Назначить цену → Order.status = priced |
| `dispute_resolve_{order_id}_refund` | Админ | Арбитраж: возврат 50% |
| `dispute_resolve_{order_id}_reject` | Админ | Арбитраж: отказ в возврате |
| `mark_executor_paid_{payment_id}` | Админ | Отметить выплату исполнителю |
| `/debts` | Админ | Список невыплаченных сумм исполнителям |

---

## 6. Frontend — изменения

### 6.1 Блок оплаты на OrderDetail

Появляется когда `order.status === "priced"`:

```
┌─────────────────────────────────────────┐
│  💰 Оплата заказа                       │
│                                         │
│  Стоимость работы:          10 000 ₽    │
│                                         │
│  🎁 Списать бонусы:                     │
│  ┌─────────────────────────┐            │
│  │ 2 000                   │  макс: 5000│
│  └─────────────────────────┘            │
│  Доступно: 5 000 бонусов                │
│                                         │
│  ─────────────────────────────────      │
│  Итого к оплате:             8 000 ₽    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │     💳 Оплатить 8 000 ₽        │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Нажимая, вы соглашаетесь с условиями   │
└─────────────────────────────────────────┘
```

### 6.2 Статусы оплаты на OrderDetail

| Статус заказа | Что видит клиент |
|---------------|------------------|
| `priced` | Блок оплаты (п. 6.1) |
| `paid` (< 1ч) | "Оплачено ✅" + кнопка "Отменить и вернуть деньги" + таймер |
| `paid` (> 1ч) | "Оплачено ✅ Ожидайте начала работы" |
| `in_progress` | Прогресс-бар |
| `done` / `confirming` | "Работа готова!" + кнопки "Подтвердить" / "Не принята" + таймер 2 дня |
| `completed` | "Заказ завершён ✅" |
| `disputed` | "На рассмотрении администратором" |
| `canceled` + refunded | "Заказ отменён. Средства возвращены." |

### 6.3 Фильтры в Orders.jsx ✅ Реализовано

```javascript
const FILTERS = [
  { id: 'all', label: 'Все' },
  { id: 'active', label: 'Активные' },       // new–disputed (всё кроме completed/canceled)
  { id: 'priced', label: 'К оплате' },
  { id: 'paid', label: 'Оплачены' },
  { id: 'in_progress', label: 'В работе' },
  { id: 'confirming', label: 'Проверка' },
  { id: 'completed', label: 'Завершены' },
  { id: 'canceled', label: 'Отменены' },
]
```

### 6.4 Новые типы уведомлений (Notifications.jsx)

| Тип | Иконка | Текст |
|-----|--------|-------|
| `price_set` | 💰 | "Цена назначена: X ₽. Оплатите заказ." |
| `payment_success` | ✅ | "Оплата получена! Работа скоро начнётся." |
| `payment_refunded` | 💸 | "Средства возвращены на карту." |
| `order_confirming` | 📋 | "Проверьте работу. 2 дня на подтверждение." |
| `order_completed` | 🎉 | "Заказ завершён!" |
| `order_disputed` | ⚠️ | "Заявка передана на рассмотрение." |
| `payment_reminder` | ⏰ | "Не забудьте оплатить заказ #X" |

### 6.5 StatusBadge — новые статусы

| Статус | Label | Цвет |
|--------|-------|------|
| `priced` | К оплате | `#f9a825` (жёлтый) |
| `paid` | Оплачен | `#4bc8e8` (голубой) |
| `confirming` | На проверке | `#f9a825` (жёлтый) |
| `completed` | Завершён | `#4caf50` (зелёный) |
| `disputed` | Спор | `#f44336` (красный) |

---

## 7. Безопасность

| Риск | Митигация |
|------|-----------|
| Подделка webhook | Проверка подписи от провайдера (IP whitelist + HMAC) |
| Повторный webhook | Идемпотентность: проверка `provider_payment_id` уникален |
| Подмена суммы оплаты | Сумма берётся из БД (order.price - bonus), не от клиента |
| Оплата чужого заказа | Проверка `order.client_id === user_id` |
| Злоупотребление возвратами | Лимит отмен на пользователя (будущее) |
| Webhook без TG-auth | Отдельный роутер, проверка подписи провайдера |
| Двойное списание бонусов | Транзакция в БД: списание + создание Payment атомарно |

---

## 8. План реализации (этапы)

### Этап 1 — Фундамент (Backend) ✅ ГОТОВО
- [x] Миграция 003: новые статусы OrderStatus, поля Order, поля Payment
- [x] `PaymentProvider` (ABC) + `MockProvider`
- [x] `PaymentService` (initiate, webhook, cancel, release, refund, set_price, confirm, dispute)
- [x] API роутер `/payments` (create, webhook, cancel, get)
- [x] Конфиг: 5 переменных в `config.py` (PAYMENT_PROVIDER, SHOP_ID, SECRET_KEY, RETURN_URL, WEBHOOK_SECRET)
- [x] Webhook исключён из TG-авторизации (`auth.py`)
- [ ] Тесты PaymentService с MockProvider

### Этап 2 — Подтверждение и арбитраж (Backend) ✅ ГОТОВО
- [x] API: `/orders/{id}/confirm`, `/orders/{id}/dispute`
- [x] Команды бота: `set_price` (executor.py), арбитраж disputed (admin.py)
- [x] `SchedulerService` (автоотмена 48ч, напоминания 12/24/36ч, автоподтверждение 2д)
- [x] Интеграция с `NotificationService` (8 новых типов + 5 новых методов)
- [x] Задолженности для админа (кнопка в админ-панели + mark_paid)

### Этап 3 — Frontend ✅ ГОТОВО
- [x] `StatusBadge` — 6 новых статусов (priced, paid, review, confirming, completed, disputed)
- [x] `OrderProgress` — 6-шаговый прогресс-бар с маппингом STATUS_TO_STEP, двойной режим (currentStep / status)
- [x] `OrderDetail` — блок оплаты (сводка, слайдер бонусов, обратный отсчёт дедлайна 48ч)
- [x] `OrderDetail` — блок после оплаты (info + кнопка отмены в окне 1ч с обратным отсчётом)
- [x] `OrderDetail` — блок подтверждения/спора (confirming/done → подтвердить / открыть спор с формой)
- [x] `OrderDetail` — статусы completed и disputed
- [x] `Orders.jsx` — фильтры: "Активные", "К оплате", "Оплачены", "В работе", "Проверка", "Завершены", "Отменены"
- [x] `Notifications.jsx` — 8 новых типов уведомлений (price_set, payment_success, payment_refunded, payment_reminder, order_completed, order_confirming, order_disputed, confirmation_reminder)
- [x] CSS: `.payment-block` со всеми модификаторами, стили новых badge-статусов, слайдер, textarea спора

### Этап 4 — Провайдер и продакшн
- [ ] Регистрация в YooKassa (или выбранный провайдер)
- [ ] `YooKassaProvider` — реализация интерфейса
- [ ] Настройка webhook URL на стороне провайдера
- [ ] Конфиг: `PAYMENT_SHOP_ID`, `PAYMENT_SECRET_KEY` в .env
- [ ] Тестовые платежи в sandbox
- [ ] Продакшн-переключение

---

## 9. Текущее состояние кодовой базы

### Создано (Этапы 1–3)

| Компонент | Файл | Описание |
|-----------|------|----------|
| PaymentProvider ABC | `backend/bot/services/payment_provider.py` | ABC + PaymentResult/RefundResult dataclasses |
| MockProvider | `backend/bot/services/providers/mock_provider.py` | Тестовый провайдер (mock_ UUID, всегда succeeded) |
| Фабрика провайдеров | `backend/bot/services/providers/__init__.py` | `get_provider(name)` → MockProvider |
| PaymentService | `backend/bot/services/payment_service.py` | 10 static-методов: initiate, webhook, cancel, release, partial_refund, confirm, dispute, set_price, get_by_order |
| SchedulerService | `backend/bot/services/scheduler_service.py` | 3 задачи: автоотмена 48ч, напоминания 12/24/36ч, автоподтверждение 2д |
| API роутер payments | `backend/api/routers/payments.py` | 4 эндпоинта: create, webhook, cancel, get |
| Pydantic-схемы | `backend/api/schemas/payment.py` | PaymentCreate, PaymentCancel, OrderConfirm, OrderDispute |
| Миграция 003 | `backend/migrations/versions/003_payments.py` | +5 OrderStatus, +8 NotificationType, +4 Order поля, +9 Payment полей |

### Изменено (Этапы 1–3)

| Компонент | Файл | Изменения |
|-----------|------|-----------|
| Модели БД | `backend/bot/db/models.py` | OrderStatus +5, NotificationType +8, Order +4 поля, Payment +9 полей (provider_payment_id переименован) |
| Конфиг | `backend/bot/config.py` | +5 переменных (PAYMENT_PROVIDER, SHOP_ID, SECRET_KEY, RETURN_URL, WEBHOOK_SECRET) |
| API auth | `backend/api/auth.py` | Webhook исключён из TG-авторизации |
| API main | `backend/api/main.py` | +payments роутер |
| Уведомления | `backend/bot/services/notification_service.py` | +5 методов (notify_payment_success, refunded, price_set, completed, disputed, reminder) |
| Хендлер исполнителя | `backend/bot/handlers/executor.py` | FSM: назначение цены (start_set_price, handle_price_input) |
| Хендлер админа | `backend/bot/handlers/admin.py` | Споры, задолженности, арбитраж (refund/reject), mark_paid |
| Роутер заказов | `backend/api/routers/orders.py` | +confirm, +dispute эндпоинты |
| Бот main | `backend/bot/main.py` | +asyncio.create_task(run_scheduler()) |
| StatusBadge | `frontend/src/components/ui/StatusBadge.jsx` | +6 статусов (priced, paid, review, confirming, completed, disputed) |
| OrderProgress | `frontend/src/components/ui/OrderProgress.jsx` | 6-шаговый прогресс, STATUS_TO_STEP маппинг, двойной режим |
| OrderDetail | `frontend/src/pages/OrderDetail.jsx` | Блоки оплаты, подтверждения, спора, завершения; загрузка платежей и профиля |
| Orders | `frontend/src/pages/Orders.jsx` | 8 фильтров (вкл. "Активные", "К оплате"), прогресс-бар по status |
| Notifications | `frontend/src/pages/Notifications.jsx` | +8 типов уведомлений для платежей |
| CSS | `frontend/src/styles/home/orders.css` | `.payment-block` со всеми модификаторами, badge-статусы |

### Осталось создать (Этап 4)

| Компонент | Файл |
|-----------|------|
| YooKassaProvider | `backend/bot/services/providers/yookassa_provider.py` |
| Тесты PaymentService | `backend/tests/test_payment_service.py` |

---

## 10. API-контракты

### POST `/api/payments/create`

**Request:**
```json
{
  "order_id": 42,
  "user_id": 927125510,
  "bonus_amount": 2000.00
}
```

**Response (200):**
```json
{
  "payment_id": 1,
  "confirmation_url": "https://yookassa.ru/pay/xxx",
  "amount": 8000.00,
  "bonus_used": 2000.00
}
```

### POST `/api/payments/webhook`

**Request** (от провайдера):
```json
{
  "event": "payment.succeeded",
  "object": {
    "id": "provider_xxx",
    "status": "succeeded",
    "amount": { "value": "8000.00" }
  }
}
```

**Response:** `200 OK` (без тела)

### POST `/api/payments/{id}/cancel`

**Request:**
```json
{ "user_id": 927125510 }
```

**Response (200):**
```json
{
  "status": "refunded",
  "refunded_amount": 8000.00,
  "bonus_returned": 2000.00
}
```

### POST `/api/orders/{id}/confirm`

**Request:**
```json
{ "user_id": 927125510 }
```

**Response (200):**
```json
{ "status": "completed" }
```

### POST `/api/orders/{id}/dispute`

**Request:**
```json
{
  "user_id": 927125510,
  "reason": "Преподаватель не принял работу"
}
```

**Response (200):**
```json
{ "status": "disputed" }
```

---

## 11. Конфигурация (.env)

```env
# ── Payments ──────────────────────────────────────
PAYMENT_PROVIDER=mock              # mock | yookassa
PAYMENT_SHOP_ID=                   # ID магазина (для yookassa)
PAYMENT_SECRET_KEY=                # Секретный ключ
PAYMENT_RETURN_URL=https://olddiamond.online/orders  # Куда вернуть после оплаты
PAYMENT_WEBHOOK_SECRET=            # Секрет для проверки подписи webhook
```
