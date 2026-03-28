---
title: "Деплой и Инфраструктура"
scope: docker-compose.yml
updated: 2026-03-13
status: actual
category: "DevOps и инфраструктура"
type: "Документация"
tags: [DevOps, Docker, Deploy]
description: "Описание Docker-сервисов, управления контейнерами и процесса автоматического деплоя на сервер."
---

# 🚀 Деплой и Инфраструктура

Проект полностью контейнеризирован с использованием **Docker Compose**, что обеспечивает стабильность работы в любой среде.

---

## 🐋 Сервисы Docker

Система состоит из 4 взаимосвязанных контейнеров:

1.  **`ngueu_db` (PostgreSQL 15)**: Хранение данных. Порт `5432` (открыт наружу, рекомендуется закрыть).
2.  **`ngueu_api` (FastAPI)**: REST API. Внутренний порт `8000`. Volume для загрузок.
3.  **`ngueu_bot` (Aiogram)**: Telegram-бот.
4.  **`ngueu_frontend` (Nginx + React)**: Раздача Mini App. Порт `3000`.

---

## 🛠 Автоматический деплой

Скрипт `deploy.sh` автоматизирует цикл обновления:
```bash
./deploy.sh
```
Он пушит код в GitLab, подключается к серверу (`158.160.202.185`) по SSH и перезапускает контейнеры.

---

## 🛠 Ручное управление сервером

### Просмотр логов
```bash
docker compose logs -f       # Все сервисы
docker compose logs -f bot   # Только бот
```

### Обновление контейнеров
```bash
docker compose pull
docker compose up -d --build
```

### Работа с БД
```bash
docker exec -it ngueu_db psql -U postgres -d ngueu_db
```

---

## 🏗 Настройка туннеля (ngrok)

Для работы HTTPS в Telegram:
```bash
npx ngrok http 3000
```
После запуска обновите URL в `@BotFather` и в `.env` на сервере.

---

## 🧹 Обслуживание
- **Бэкап БД**: `docker exec ngueu_db pg_dump -U postgres ngueu_db > backup.sql`
- **Очистка**: `docker system prune -a`
