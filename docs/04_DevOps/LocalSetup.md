---
title: "Локальный запуск"
scope: requirements.txt
updated: 2026-03-13
status: actual
category: "DevOps и инфраструктура"
type: "Документация"
tags: [DevOps, Backend, Frontend, Config]
description: "Пошаговое руководство по запуску всех компонентов проекта локально без Docker."
---

# 🚀 Руководство по локальному запуску

Для полноценной работы необходимо запустить три процесса параллельно.

---

## Шаг 0: Подготовка
```bash
# Активация окружения и установка зависимостей
source .venv/bin/activate
pip install -r requirements.txt

# Применение миграций БД
alembic upgrade head
```

---

## Шаг 1: Запуск API (Порт 8000)
```bash
export PYTHONPATH="$(pwd)/backend/bot"
uvicorn backend.api.main:app --reload --port 8000
```

---

## Шаг 2: Запуск Фронтенда (Порт 3000)
```bash
cd frontend
npm install
npm run dev
```

---

## Шаг 3: Настройка туннеля (ngrok)
Необходим для работы HTTPS внутри Telegram. Пробрасываем порт Vite (3000):
```bash
npx ngrok http 3000
```
**Важно:** Полученную ссылку нужно прописать в BotFather и в файл `.env` (переменная `MINIAPP_URL`).

---

## 🛠 Полезные утилиты

### Сброс базы данных
```bash
python backend/utils/scripts/reset_db.py
alembic upgrade head
```
