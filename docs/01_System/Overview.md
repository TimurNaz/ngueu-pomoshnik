---
title: "Обзор системы"
scope: docs/01_System/Overview.md
updated: 2026-03-13
status: actual
category: "Архитектура и система"
type: "Документация"
tags: [Backend, Frontend, API, Infrastructure]
description: "Общий обзор архитектуры проекта НГУЭУ/Помощник, описание компонентов и схемы взаимодействия."
---

# 🎓 НГУЭУ / Помощник — Общее описание системы

Этот документ является "точкой входа" в проект и описывает его общую архитектуру на март 2026 года.

---

## 🏗 Архитектура системы

Проект построен по модульному принципу и состоит из четырех ключевых компонентов:

1.  **Telegram Bot (aiogram 3)**: Интерфейс взаимодействия с пользователем внутри мессенджера. Отвечает за приветствие, базовую навигацию и запуск Mini App.
2.  **Web Mini App (React + Vite)**: Современный SPA-интерфейс для оформления заявок, просмотра истории заказов и управления профилем.
3.  **RestAPI (FastAPI)**: "Сердце" системы. Служит мостом между фронтендом и базой данных. Обеспечивает валидацию данных и бизнес-логику.
4.  **Database (PostgreSQL + SQLAlchemy)**: Единое хранилище данных для бота и Mini App.

### Схема взаимодействия:
`Пользователь <-> Telegram Bot <-> Mini App <-> FastAPI <-> PostgreSQL`

---

## 📁 Структура директорий

```
ngueu-pomoshnik/
├── backend/
│   ├── api/                    # [FastAPI]
│   │   └── main.py             # Точка входа API, эндпоинты, CORS, статика
│   ├── bot/                    # [Aiogram]
│   │   ├── main.py             # Запуск бота и регистрация роутеров
│   │   ├── config.py           # Настройки бота (токены, права)
│   │   ├── db/                 # Слой данных
│   │   │   ├── models.py       # SQLAlchemy модели (User, Order)
│   │   │   ├── database.py     # Инициализация Engine и SessionLocal
│   │   │   └── redis.py        # Конфигурация Redis для FSM
│   │   ├── handlers/           # Обработчики (логика команд)
│   │   │   ├── client.py       # Основное меню и запуск Mini App
│   │   │   ├── admin.py        # Панель управления
│   │   │   ├── executor.py     # Логика для исполнителей
│   │   │   └── common.py       # Общие команды (/start, /help)
│   │   ├── keyboards/          # Интерфейс бота
│   │   │   ├── client.py       # Reply и Inline кнопки
│   │   │   └── faq_data.py     # Статические данные для FAQ
│   │   ├── services/           # Бизнес-слой
│   │   │   ├── user_service.py # Работа с профилем и бонусами
│   │   │   └── db_service.py   # Общие CRUD операции
│   │   └── states/             # Машина состояний
│   │       └── consent.py      # Стейты для соглашений
│   ├── utils/                  # Утилиты и системные скрипты
│   │   └── scripts/
│   │       ├── reset_db.py     # Полный сброс базы (Drop All)
│   │       └── init_db.py      # Первичная инициализация (Create All)
│   ├── migrations/             # [Alembic]
│   │   └── versions/           # Скрипты миграций БД
│   └── static/uploads/         # Пользовательский контент (PDF, PNG)
├── frontend/                   # [React + Vite]
│   ├── src/
│   │   ├── App.jsx             # Маршрутизация Mini App
│   │   ├── main.jsx            # Точка монтирования React
│   │   ├── config.js           # Базовые URL и константы
│   │   ├── components/         # UI Kit (Header, Layout, Nav)
│   │   ├── hooks/
│   │   │   └── useTelegram.js  # Интеграция с Telegram WebApp API
│   │   ├── pages/              # Экраны
│   │   │   ├── Home.jsx        # Главная / Приветствие
│   │   │   ├── NewOrder.jsx    # Форма создания заказа (3 шага)
│   │   │   ├── Orders.jsx      # Список заявок пользователя
│   │   │   └── Profile.jsx     # Личный кабинет / Бонусы
│   │   └── styles/             # CSS (Variables, Global)
│   └── index.html              # HTML-шаблон
├── docs/                       # База знаний
│   ├── INDEX.md                # Карта всех документов
│   ├── 01_System/              # Overview.md, DataModel.md
│   ├── 02_Backend/             # API.md, Bot.md, Services.md
│   ├── 03_Frontend/            # Config.md, Structure.md
│   ├── 04_DevOps/              # Deploy.md, Secrets.md, LocalSetup.md
│   └── 99_State/               # Changelog.md, Issues.md
├── docker-compose.yml          # Оркестрация (db, api, bot, frontend)
└── deploy.sh                   # Скрипт деплоя на сервер
```

---

## 🚀 Инфраструктура (Docker Compose)

Проект работает в Docker-контейнерах, обеспечивая изоляцию и легкий деплой.

| Сервис | Образ | Порты | Назначение |
|--------|-------|-------|------------|
| **db** | `postgres:15-alpine` | 5432 (внутр.) | Основная база данных |
| **api** | `Custom (FastAPI)` | 8000 | REST API для MiniApp |
| **bot** | `Custom (Aiogram)` | - | Телеграм-бот (Polling) |
| **frontend** | `Custom (React/Nginx)` | 3000 (внешн.) | Web Mini App интерфейс |
