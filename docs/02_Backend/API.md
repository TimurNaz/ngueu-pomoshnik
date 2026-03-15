---
title: "Справочник API"
scope: backend/api/main.py
updated: 2026-03-13
status: actual
category: "Разработка"
type: "Документация"
tags: [Backend, API, Integration]
description: "Детальное описание эндпоинтов REST API (FastAPI) для взаимодействия с Telegram Mini App."
---

# 📡 Справочник API (REST API Reference)

Данный документ описывает доступные эндпоинты FastAPI для взаимодействия с Mini App и внешними сервисами.

---

## 🏗 Общая информация

- **Базовый URL**: `https://your-domain.com/api` (или `http://localhost:8000/api`)
- **Формат данных**: JSON
- **Статика**: Доступна по пути `/static/uploads/{filename}`
- **Интеграция с ботом**: Создание заказа автоматически триггерит уведомление администраторам через Telegram.

---

## 🩺 Системные эндпоинты

### Проверка работоспособности
`GET /api/health`
- **Пример ответа**:
  ```json
  {
    "status": "ok",
    "timestamp": "2026-03-13T12:00:00Z"
  }
  ```

---

## 📂 Работа с файлами

### Загрузка вложения
`POST /api/upload`
- **Описание**: Загрузка изображений или документов (PDF, DOCX).
- **Ограничения**: Максимальный размер файла — **30 МБ**.
- **Пример ответа**:
  ```json
  {
    "filename": "original_name.png",
    "file_url": "/static/uploads/uuid-name.png"
  }
  ```

---

## 👤 Пользователи (Users)

### Получение профиля
`GET /api/users/{user_id}`
- **Описание**: Возвращает данные пользователя, баланс бонусов и уровень лояльности.
- **Пример ответа**:
  ```json
  {
    "id": 8360967543,
    "username": "ivan_ivanov",
    "role": "client",
    "bonus_balance": 500.0,
    "loyalty_level": "novice",
    "total_spent": 0.0
  }
  ```

---

## 📦 Заказы (Orders)

### Создание заказа
`POST /api/orders`
- **Описание**: Создает новую заявку. После успеха API вызывает `UserService.send_admin_alert`.
- **Тело запроса (JSON)**:
  ```json
  {
    "client_id": 8360967543,
    "work_type": "essay",
    "subject": "Экономика",
    "topic": "Цифровизация банков",
    "deadline": "2026-04-01T10:00:00Z",
    "urgency": "one_week",
    "attachments": ["/static/uploads/file1.png"]
  }
  ```
- **Пример ответа (201 Created)**:
  ```json
  {
    "status": "success",
    "order_id": 42
  }
  ```

### Список заказов клиента
`GET /api/orders/client/{client_id}`

### Последние заказы
`GET /api/orders/latest/{client_id}` (возвращает 3 последних заказа)

---

## ⚠️ Безопасность
На текущий момент API не требует авторизации. **Задача на следующую итерацию**: внедрить валидацию `X-TG-Init-Data`.

