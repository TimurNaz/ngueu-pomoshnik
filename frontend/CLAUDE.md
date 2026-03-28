# CLAUDE.md — НГУЭУ/Помощник Frontend Design System

> Документ для интеграции Figma → Code через Model Context Protocol
> Обновлено: 2026-03-22 (добавлены уведомления, обновлены роуты и API)

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

### Figma-палитра (хардкод в компонентах)

```css
/* Используются напрямую вместо CSS-переменных для точного соответствия Figma */
#65a4f9              /* Синий акцент (аватар, action-card--primary, info-card--blue) */
#4bc8e8 → #5bd4f0   /* Голубой градиент (бонусная карта) */
#c3fe4c              /* Зелёный CTA (активные фильтры, кнопки навбара) */
#fafafa              /* Фон страниц */
#fff                 /* Фон карточек */
#1a1a1a              /* Основной текст */
#8e8e8e              /* Muted текст */
rgba(0,0,0,0.04-0.06) /* Бордеры и тени */
```

### Нейтральные

```css
--bg: #f4f4f4              /* Фон страниц (legacy, новые страницы используют #fafafa) */
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

/* Figma: основной радиус карточек — 12-16px, бонусная карта — 24px */
```

### Тени

```css
--shadow-sm: 0 2px 8px rgba(0,0,0,0.05)
--shadow-md: 0 4px 16px rgba(0,0,0,0.08)
--shadow-accent: 0 6px 20px rgba(75,200,232,0.18)
--shadow-green: 0 4px 12px rgba(183,243,74,0.30)

/* Figma: основная тень карточек — 0 4px 16px rgba(0,0,0,0.06) */
```

---

## Статические ресурсы (`public/images/`)

```
public/images/
├── logo.png              — Логотип nG (используется в Header и action-card FAQ)
├── mascot.png            — Робот-маскот (бонусная карта на главной)
├── chevron-right.svg     — Зелёная стрелка (info-card, order-card)
├── nguey-logo.svg        — Текстовый логотип NGUEY (#65A4F9, footer)
├── nav/                  — SVG-иконки навигации (из Figma icon pack)
│   ├── home.svg
│   ├── document.svg
│   ├── add.svg
│   ├── comment-info.svg
│   └── user.svg
└── onboarding/           — SVG-иллюстрации для онбординга (4 слайда)
    ├── slide1.svg
    ├── slide2.svg
    ├── slide3.svg
    └── slide4.svg
```

---

## Компоненты

### Структура директорий

```
src/
├── components/
│   ├── Layout.jsx          — Header + Outlet + BottomNav
│   ├── Header.jsx          — Шапка (sticky, glassmorphism blur)
│   ├── BottomNav.jsx       — Нижняя навигация (5 вкладок, SVG-иконки)
│   ├── ui/
│   │   ├── OrderProgress.jsx   — Прогресс-бар 4 этапа
│   │   └── StatusBadge.jsx     — Бейдж статуса заявки
├── pages/
│   ├── Onboarding.jsx      — Приветственный экран (4 слайда, свайп, анимация)
│   ├── Home.jsx            — Главная клиента
│   ├── NewOrder.jsx        — Форма заявки (3 шага)
│   ├── OrderResult.jsx     — Результат отправки заявки
│   ├── Orders.jsx          — Список заявок с фильтрами
│   ├── OrderDetail.jsx     — Детальная страница заявки
│   ├── Notifications.jsx   — Уведомления (API, mark read)
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

## Header (`components/Header.jsx`)

- Логотип: `<img src="/images/logo.png">` вместо эмодзи
- Glassmorphism: `background: rgba(255,255,255,0.65); backdrop-filter: blur(20px)`
- Sticky top, z-index 100
- Колокольчик уведомлений: навигация на `/notifications`, бейдж `.header__badge` с кол-вом непрочитанных
- Бейдж: красный кружок (`#f44336`), позиция `top: -4px; right: -4px`, обновляется каждые 30 сек через API

---

## Bottom Navigation (`components/BottomNav.jsx`)

- SVG-иконки из `/images/nav/` вместо эмодзи
- Без текстовых лейблов — только иконки в квадратных обёртках
- Glassmorphism как у Header
- Иконки в `.bottom-nav__icon-wrap`: `40x40px`, `border-radius: 12px`, фон `#f3f2ee`
- Обводка: `0.5px solid rgba(0,0,0,0.04)` (еле заметная)
- Активная: `background: #c3fe4c`, `transform: scale(1.08)`, зелёная тень

```jsx
<div className="bottom-nav__icon-wrap">
  <img src={icon} alt={label} className="bottom-nav__icon" />
</div>
```

---

## Главная страница (`pages/Home.jsx`)

### Приветствие
```jsx
<h1 className="greeting__title">
  Привет, <span className="greeting__name">{displayName}!</span>
</h1>
```
- Размер: 32px, вес заголовка 600, имя 200 (тонкий)
- Аватар: квадрат 46px, `border-radius: 12px`, фон `#65a4f9`

### Бонусная карта
- Градиент: `linear-gradient(155deg, #4bc8e8, #5bd4f0)`
- Радиус: 24px, внутреннее белое свечение через `inset box-shadow`
- Маскот: `<img src="/images/mascot.png">`, абсолютное позиционирование справа
- ID бейдж: полупрозрачный `rgba(255,255,255,0.2)` с `backdrop-filter: blur(6px)`
- CTA кнопка: зелёная `#c3fe4c`

### Быстрые действия (2x2 grid)
4 карточки с уникальными декоративными эффектами:

| Модификатор | Стиль | Декор |
|---|---|---|
| `--primary` | Синий `#65a4f9` | Круг `::after` в правом верхнем углу |
| `--green` | Неоморфизм `#d4ff80 → #a8f040` | Двойная тень + стеклянная подсветка `::after` |
| `--surface` | Белый `#fafafa` | Повёрнутый квадрат + watermark-логотип |
| `--light` | Голубой `rgba(101,164,249,0.08)` | Точечный паттерн `radial-gradient` |

### Превью заявок
- Показывается всегда (есть заявки или нет)
- Пустое состояние: иконка 📭, текст, подсказка
- Модификатор: `.orders-preview--empty` с пунктирной рамкой

### О сервисе (info-card)
3 карточки с цветовыми темами:

| Модификатор | Цвет | Содержание |
|---|---|---|
| `--yellow` | `#fff8e1` / `#f9a825` | Отзывы → t.me/ngueu_reviews |
| `--blue` | `rgba(101,164,249,0.08)` / `#65a4f9` | Новости и акции → t.me/ngueu_helper_bot |
| `--green` | `rgba(183,243,74,0.08)` / `#6abf40` | Сотрудничество → t.me/ngueu_bot_support |

Стрелка: `<img src="/images/chevron-right.svg">`

### Footer
- Логотип NGUEY как водяной знак (opacity 0.15, 90% ширины)
- Кнопки TG / VK
- Email, Copyright

---

## Страница заявок (`pages/Orders.jsx`)

### Заголовок
```jsx
<h1 className="orders-page__title">Мои заявки</h1>
<p className="orders-page__count">5 заявок</p>
```

### Фильтры
- Скруглённые чипы (`border-radius: 12px`), белый фон, мягкая тень
- Активный: зелёный `#c3fe4c` с тенью
- Горизонтальный скролл, скрытый скроллбар

### Карточки заявок
- Фон `#fff`, радиус `16px`, тень `0 4px 16px rgba(0,0,0,0.06)`
- Синий градиент-акцент сверху при нажатии (`::before`)
- ID в бейдже с фоном `rgba(0,0,0,0.04)`
- Footer с разделительной линией
- Стрелка: `<img src="/images/chevron-right.svg">`

### Пустое состояние
- Карточка с пунктирной рамкой (`border: 1.5px dashed`)
- Иконка 📭, текст, CTA-кнопка

### Детальная страница
- Hero-карточка с синим градиент-акцентом сверху (`::before`)
- Номер заявки в бейдже
- Список деталей: белые карточки с `border-radius: 16px`

### Блок исполнителя
- Аватар: `border-radius: 14px`, градиент `#65a4f9 → #4bc8e8`, синяя тень
- Бейдж: `rgba(75,200,232,0.12)`, цвет `#0a5f7a`, `border-radius: 20px`

---

## Уведомления (`pages/Notifications.jsx`)

- Данные из API: `GET /api/notifications/{userId}`
- Типы уведомлений (enum `NotificationType`):

| Тип | Иконка | Цвет карточки |
|---|---|---|
| `order_created` | 📝 | blue |
| `executor_assigned` | 👤 | accent |
| `order_in_progress` | ⚙️ | accent |
| `order_review` | 👀 | yellow |
| `order_done` | ✅ | green |
| `order_canceled` | ❌ | red |
| `bonus` | 🎁 | yellow |
| `system` | ⚙️ | neutral |

- Карточка `.notification-card`: белый фон, `border-radius: 16px`, тень `0 2px 8px`
- Непрочитанное `.notification-card--unread`: голубой бордер `rgba(101,164,249,0.15)`, точка-индикатор `.notification-card__dot`
- Пустое состояние: пунктирная рамка, иконка 🔔
- Действия: клик → пометить прочитанным + переход к заявке; "Прочитать все" → `POST /read-all`
- Функция `timeAgo()`: относительное время на русском

---

## Онбординг (`pages/Onboarding.jsx`)

- 4 слайда (вместо 3-х) с SVG-иллюстрациями
- Свайп-навигация (touch events, threshold 50px)
- Анимация перехода (280ms, slide left/right)
- Предзагрузка изображений
- Цветовые темы слайдов: красный, светлый, голубой, светлый
- Декоративные эллипсы на фоне
- Точечная пагинация + кнопки "Пропустить" / "Далее" / "Начать"

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
| `/onboarding` | Онбординг (4 слайда) |
| `/` | Главная |
| `/new-order` | Форма заявки |
| `/orders` | Список заявок |
| `/orders/:id` | Детальная заявка |
| `/order-result` | Результат отправки заявки |
| `/notifications` | Уведомления |
| `/faq` | FAQ |
| `/profile` | Профиль |

Онбординг показывается один раз — флаг `localStorage.onboarding_done`.

---

## Интеграция с Backend

| Действие | Метод | Путь |
|---|---|---|
| Профиль пользователя | GET | `/api/users/{userId}` |
| История бонусов | GET | `/api/users/{userId}/bonuses` |
| Реферальный код | GET | `/api/users/{userId}/referral` |
| Последние заявки | GET | `/api/orders/latest/{userId}` |
| Список заявок клиента | GET | `/api/orders/client/{userId}` |
| Детали заявки | GET | `/api/orders/{id}` |
| Создать заявку | POST | `/api/orders` |
| Отменить заявку | POST | `/api/orders/{id}/cancel` |
| Загрузить файл | POST | `/api/upload` |
| Список уведомлений | GET | `/api/notifications/{userId}` |
| Кол-во непрочитанных | GET | `/api/notifications/{userId}/unread-count` |
| Пометить прочитанным | POST | `/api/notifications/{id}/read?user_id={userId}` |
| Пометить все прочитанными | POST | `/api/notifications/{userId}/read-all` |

---

## Общие паттерны UI (Figma design system)

### Карточки
- Фон: `#fff`, бордер: `1px solid rgba(0,0,0,0.04)`
- Радиус: `16px` (стандарт), `24px` (бонусная карта)
- Тень: `0 4px 16px rgba(0,0,0,0.06)`
- При нажатии: `transform: scale(0.97-0.98)`

### Glassmorphism (Header, BottomNav)
- `background: rgba(255,255,255,0.65)`
- `backdrop-filter: blur(20px)`
- `-webkit-backdrop-filter: blur(20px)`

### Цветовые акценты
- Синий: `#65a4f9` — аватары, primary-карточки, info-card--blue
- Голубой: `#4bc8e8 → #5bd4f0` — бонусная карта, исполнитель
- Зелёный: `#c3fe4c` — CTA, активные фильтры, навбар
- Неоморфизм: `linear-gradient(145deg, #d4ff80, #a8f040)` — action-card--green

### Декоративные эффекты
- `::before` / `::after` — круги, повёрнутые квадраты, градиентные полосы
- Точечный паттерн: `radial-gradient(circle, currentColor 0.8px, transparent 0.8px)`
- Watermark: логотип с низкой opacity, rotated

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

---

## Временные элементы

- `frontend/index.html` содержит скрипт Figma HTML-to-Design capture (удалить после завершения переноса в Figma)
