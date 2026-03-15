---
title: "Модель данных"
scope: docs/01_System/DataModel.md
updated: 2026-03-13
status: actual
category: "Архитектура и система"
type: "Документация"
tags: [Backend, Database, Security]
description: "Описание структуры таблиц PostgreSQL, перечислений (Enums) и бизнес-логики финансовых расчетов."
---

# 🗄 Модель данных (База данных)

В этом документе описана структура базы данных PostgreSQL и бизнес-логика финансовых расчетов.

---

## 🏗 Список таблиц

| Модель | Назначение | Связи |
|--------|------------|-------|
| **User** | Хранение профилей (ТГ ID, роль, баланс) | loyalty, referral, timestamps |
| **ExecutorProfile** | Доп. данные для исполнителей | 1:1 с User, специализации, рейтинг |
| **Order** | Заявки на работы | client_id, executor_id, финансовые поля |
| **Payment** | Транзакции оплаты (YooKassa) | order_id, user_id |
| **BonusTransaction** | История начисления и списания бонусов | user_id, order_id |
| **Referral** | Связи пригласивший-приглашенный | referrer_id, referred_id |
| **Review** | Отзывы по заказам | order_id, NPS score |
| **HolidayBonus** | Триггеры для праздничных начислений | target levels, trigger date |
| **KnowledgeBase** | Ответы FAQ и база знаний | dept, author_id |

---

## 🔢 Перечисления (Enums)

Система использует строгие перечисления для статусов и типов данных:
1.  **UserRole**: `client`, `executor`, `admin`
2.  **LoyaltyLevel**: `base`, `bronze`, `silver`, `gold`
3.  **OrderStatus**: `pending`, `accepted`, `in_progress`, `review`, `completed`, `cancelled`
4.  **PaymentStatus**: `pending`, `succeeded`, `failed`, `canceled`
5.  **PaymentStage**: `prepayment` (50%), `full_payment` (100%)
6.  **UrgencyLevel**: `three_days`, `one_week`, `two_weeks`, `one_month`
7.  **WorkType**: `term_paper`, `thesis`, `exam`, `essay` и др.
8.  **BonusType**: `cashback`, `referral`, `registration`, `holiday`, `spend`

---

## 💰 Бизнес-константы (Финансы)

### 💎 Уровни лояльности
| Уровень | Порог трат | Кэшбэк (%) |
| :--- | :--- | :--- |
| **Base** | 0 - 10,000₽ | 3% |
| **Bronze** | 10,001 - 30,000₽ | 5% |
| **Silver** | 30,001 - 70,000₽ | 7% |
| **Gold** | 70,001₽ + | 10% |

### 🎁 Бонусная программа
*   **Регистрация**: 500₽ на бонусный счет сразу.
*   **Реферал**: 100₽ пригласившему после первой оплаты друга.
*   **Оплата бонусами**: Можно оплатить до **50%** от стоимости заказа.
*   **Комиссия сервиса**: 10% с каждого заказа.
