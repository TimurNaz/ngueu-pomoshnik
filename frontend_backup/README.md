# MiniApp (frontend)

Telegram Mini App для НГУЭУ Помощник. Открывается по кнопке **«Открыть приложение»** в боте (Личный кабинет или О нас).

## Стек и структура

- **Vite + React** — сборка и компоненты
- **React Router** — маршруты
- **CSS** — переменные в `variables.css`, общие стили в `global.css`, стили компонентов в `styles/components/` (один файл — один компонент)

## Архитектура директорий

Структура без лишней вложенности: всё в `src/`, разнесено по ролям.

```
frontend/
├── index.html              # Точка входа HTML (Vite)
├── vite.config.js          # Порт 3000, сборка в dist/
├── package.json
├── eslint.config.js
├── public/                    # Статика по URL (favicon, изображения для ссылок)
│
└── src/
    ├── main.jsx                # Вход: React, Router, подключение стилей
    ├── App.jsx                 # Маршруты (вложенные: Layout → страницы)
    │
    ├── components/              # Переиспользуемый UI (Layout, карточки, кнопки)
    │   ├── Layout.jsx           # Оболочка: Header + Outlet + Footer
    │   ├── Header.jsx
    │   ├── Footer.jsx
    │   ├── Card.jsx
    │   └── Section.jsx
    │
    ├── pages/                  # Один файл = один экран (роут)
    │   └── Home.jsx
    │
    ├── hooks/                  # Хуки (Telegram, позже — данные, формы)
    │   └── useTelegram.js
    │
    ├── styles/                 # Стили: один вход — index.css
    │   ├── index.css           # Импорт переменных, global, components
    │   ├── variables.css       # Тема, --accent, --radius и т.д.
    │   ├── global.css          # reset, body, .app, .main
    │   └── components/         # header.css, card.css, section.css, footer.css
    │
    └── assets/                 # Картинки/шрифты, импортируемые в JS (import img from '…')
```

**Куда что класть сейчас**

| Что добавляешь                         | Куда                                                      |
| -------------------------------------- | --------------------------------------------------------- |
| Новый экран                            | `pages/Имя.jsx` + маршрут в `App.jsx`                     |
| Кнопка, карточка, поле ввода           | `components/`                                             |
| Стили компонента                       | `styles/components/имя.css` + импорт в `styles/index.css` |
| Хук (запросы, Telegram, форма)         | `hooks/`                                                  |
| Картинка для `import` в коде           | `assets/`                                                 |
| Файл по прямой ссылке (favicon и т.п.) | `public/`                                                 |

**Когда приложение вырастет** (без срочности):

- **api/** — функции вызова бэкенда (`getOrders`, `createOrder`).
- **lib/** или **utils/** — чистые хелперы (формат даты, валидация).
- **components/** можно разнести на `ui/` (Card, Button), `layout/` (Header, Footer), `features/` (OrderForm и т.д.), когда файлов станет 15+.

Лишнего в текущей разметке нет: каждая папка и слой имеют одну роль, дублирования нет.

## Пайплайн (скрипты)

| Команда           | Действие                                                     |
| ----------------- | ------------------------------------------------------------ |
| `npm install`     | Установка зависимостей                                       |
| `npm run dev`     | Запуск dev-сервера на **http://localhost:3000** (hot reload) |
| `npm run build`   | Сборка в `dist/` (деплой этой папки)                         |
| `npm run preview` | Локальный просмотр собранного `dist/` на порту 3000          |
| `npm run lint`    | Проверка кода ESLint                                         |

Для разработки: `npm run dev`. Для открытия в Telegram нужен HTTPS (ngrok и т.д.).

## Локальный запуск и Telegram

0. Запустить "backend/bot" в main.py
1. Запусти приложение: в папке `frontend` выполни `npm run dev` (порт 3000).
2. Подними HTTPS-туннель: в другом терминале `npx ngrok http 3000`.
3. В **`backend/bot/.env`** пропиши: `MINIAPP_URL=https://твой-ngrok-адрес` (без слэша в конце).
4. Перезапусти бота и в Telegram открой приложение по кнопке.

Продакшен: собери проект (`npm run build`), залей содержимое `dist/` на хостинг и укажи этот HTTPS-URL в `MINIAPP_URL`.

## Ошибка -102 в Telegram

- В браузере: проверь, что запущен `npm run dev` и открыт http://localhost:3000.
- В Telegram: Mini App открывается только по **HTTPS**. Используй ngrok или другой туннель и пропиши `MINIAPP_URL` в `.env`.
