# CLAUDE.md — НГУЭУ/Помощник Frontend Design System

> Документ для интеграции Figma → Code через Model Context Protocol

---

## Стек

| Слой | Технология |
|---|---|
| Фреймворк | React 18 + Vite 5 |
| Роутинг | React Router v6 (createBrowserRouter) |
| Стили | CSS Custom Properties (без CSS Modules, без Tailwind) |
| Telegram | `window.Telegram.WebApp` SDK |
| Сборка | `npm run dev` → порт 3000 |

---

## Дизайн-токены (`src/styles/variables.css`)

### Основные цвета

```css
--accent: #0a5f7a          /* Главный цвет бренда (синий-зелёный) */
--accent-dark: #084e65     /* Тёмный акцент */
--accent-light: #4bc8e8    /* Светлый акцент */
--accent-soft: rgba(10,95,122,0.10)  /* Фоновый акцент */

--green: #b7f34a           /* CTA / активные элементы */
--green-dark: #a3db2f      /* Hover для зелёного */
--green-soft: rgba(183,243,74,0.15)

--blue-gradient-start: #4bc8e8
--blue-gradient-end:   #5bd4f0
```

### Нейтральные

```css
--bg: #f4f4f4              /* Фон страниц */
--surface: #ffffff         /* Фон карточек */
--surface-2: #f8f8f8       /* Вторичный фон */
--border: rgba(0,0,0,0.08)
--text-primary: #1d1d1f
--text-secondary: #555
--text-muted: #999
```

### Статусы заявок

```css
--status-new:      #b7f34a  / text: #0a5f7a   /* Новая */
--status-progress: #f9a825  / text: #7a4f00   /* В работе */
--status-done:     #4bc8e8  / text: #0a5f7a   /* Выполнена */
--status-canceled: #f44336  / text: #fff      /* Отменена */
```

### Радиусы

```css
--radius-xs: 6px   --radius-sm: 10px   --radius: 14px
--radius-md: 18px  --radius-lg: 24px   --radius-xl: 32px
--radius-full: 9999px
```

### Тени

```css
--shadow-sm: 0 2px 8px rgba(0,0,0,0.05)
--shadow-md: 0 4px 16px rgba(0,0,0,0.08)
--shadow-accent: 0 6px 20px rgba(75,200,232,0.18)
--shadow-green: 0 4px 12px rgba(183,243,74,0.30)
```

---

## Компоненты

### Структура директорий

```
src/
├── components/
│   ├── Layout.jsx          — Header + Outlet + BottomNav
│   ├── Header.jsx          — Шапка (sticky, blur)
│   ├── BottomNav.jsx       — Нижняя навигация (5 вкладок)
│   ├── ui/
│   │   ├── OrderProgress.jsx   — Прогресс-бар 4 этапа
│   │   └── StatusBadge.jsx     — Бейдж статуса заявки
│   └── onboarding/
│       ├── Screen1.jsx / Screen2.jsx / Screen3.jsx
├── pages/
│   ├── Onboarding.jsx      — Приветственный экран (3 слайда)
│   ├── Home.jsx            — Главная клиента
│   ├── NewOrder.jsx        — Форма заявки (3 шага)
│   ├── Orders.jsx          — Список заявок с фильтрами
│   ├── OrderDetail.jsx     — Детальная страница заявки
│   ├── FAQ.jsx             — Аккордеон вопросов
│   └── Profile.jsx         — Профиль пользователя
└── hooks/
    └── useTelegram.js      — Обёртка над Telegram WebApp API
```

### Паттерн CSS-классов (BEM)

```
.block {}
.block__element {}
.block--modifier {}
```

Примеры: `.order-card`, `.order-card__title`, `.btn--primary`, `.badge--done`

---

## Кнопки

```jsx
<button className="btn btn--primary">Основная</button>
<button className="btn btn--green">CTA / Отправить</button>
<button className="btn btn--outline">Второстепенная</button>
<button className="btn btn--ghost">Призрак</button>
<button className="btn btn--sm btn--auto">Маленькая</button>
```

---

## Статус-бейджи

```jsx
import StatusBadge from './components/ui/StatusBadge'
<StatusBadge status="new" />          // 🆕 Новая
<StatusBadge status="in_progress" />  // ⚙️ В работе
<StatusBadge status="done" />         // ✅ Выполнена
<StatusBadge status="canceled" />     // ❌ Отменена
```

---

## Прогресс-бар заявки

```jsx
import OrderProgress from './components/ui/OrderProgress'
<OrderProgress currentStep={2} />
// 0 = Новая, 1 = Исполнитель назначен, 2 = В работе, 3 = Выполнено
```

---

## Telegram-хук

```jsx
import { useTelegram } from '../hooks/useTelegram'
const { user, haptic, expand, close } = useTelegram()

haptic('impact', 'light')        // Тактильная отдача
haptic('notification', 'success') // Успешное действие
```

---

## Роутинг

| Путь | Страница |
|---|---|
| `/onboarding` | Онбординг (3 слайда) |
| `/` | Главная |
| `/new-order` | Форма заявки |
| `/orders` | Список заявок |
| `/orders/:id` | Детальная заявка |
| `/faq` | FAQ |
| `/profile` | Профиль |

Онбординг показывается один раз — флаг `localStorage.onboarding_done`.

---

## Интеграция с Backend

Все mock-данные помечены комментарием `// TODO: заменить на API-запрос`.

| Действие | Метод | Путь |
|---|---|---|
| Список заявок | GET | `/api/requests` |
| Детали заявки | GET | `/api/requests/:id` |
| Создать заявку | POST | `/api/requests` |
| Профиль | GET | `/api/users/me` |

---

## Запуск

```bash
cd frontend
npm install
npm run dev    # http://localhost:3000

# Для Telegram WebApp нужен HTTPS:
npx ngrok http 3000
# Вставить URL в backend .env → MINIAPP_URL=https://...
```
