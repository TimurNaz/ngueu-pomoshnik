---
title: "Конфигурация фронтенда"
scope: frontend/vite.config.js
updated: 2026-03-13
status: actual
category: "Разработка"
type: "Документация"
tags: [Frontend, Config, API]
description: "Настройки Vite, проксирование запросов к API и подключение Telegram WebApp SDK."
---

# ⚙️ Конфигурация и Связь с API

Фронтенд использует Vite в качестве сборщика и сервера разработки.

---

## 🛠 Vite Config (`vite.config.js`)

Основные параметры сервера разработки:
- **Port**: `3000`
- **Host**: `true` (Разрешает внешние подключения для ngrok/tunnel).
- **Allowed Hosts**: `true` (Снимает ограничения по доменам).

### Proxy
Для обхода CORS в режиме разработки настроено проксирование:
- Все запросы, начинающиеся с `/api`, перенаправляются на `http://localhost:8000`.

---

## 📡 Подключение к API (`src/config.js`)

Файл `src/config.js` определяет базовый URL для запросов. 
**Важно**: В режиме разработки используется `/api` (через прокси), в продакшне — абсолютный URL сервера.

---

## 📱 Telegram SDK

В `index.html` подключен скрипт:
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```
Доступ к SDK осуществляется через кастомный хук `src/hooks/useTelegram.js`, который предоставляет:
- `user`: Данные текущего пользователя.
- `initData`: Строка для валидации на бэкенде.
- `haptic`: Методы для вибрации устройства.
- `expand()` / `close()`: Управление окном Mini App.

---

## 🚀 Сборка и Деплой

- **Команда разработки**: `npm run dev` (порт 3000).
- **Команда сборки**: `npm run build` (результат в папке `dist`).
- **Nginx**: В Docker-контейнере статика раздается через Nginx, настроенный на `try_files $uri $uri/ /index.html`.
