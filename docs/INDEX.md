# 🎓 НГУЭУ / Помощник — База знаний

Добро пожаловать в центральный узел документации проекта. Здесь собрана вся информация об архитектуре, процессах разработки и текущем состоянии системы.

---

## 🚀 Основная информация
- **Стек**: Aiogram 3 + FastAPI + React + PostgreSQL
- **Версия**: 1.1.0 (MVP)
- **Последнее обновление**: 2026-03-13

---

## 🗺 Карта документов

| Путь | Description | Status |
| :--- | :--- | :--- |
| [01_System/Overview.md](01_System/Overview.md) | Общий обзор архитектуры и взаимодействия компонентов | ✅ Actual |
| [01_System/DataModel.md](01_System/DataModel.md) | Схема базы данных и описание сущностей | ✅ Actual |
| [02_Backend/API.md](02_Backend/API.md) | Справочник эндпоинтов REST API | ✅ Actual |
| [02_Backend/Bot.md](02_Backend/Bot.md) | Логика Telegram-бота, команды и клавиатуры | ✅ Actual |
| [02_Backend/Services.md](02_Backend/Services.md) | Описание бизнес-логики (бонусы, лояльность) | ✅ Actual |
| [03_Frontend/Structure.md](03_Frontend/Structure.md) | Архитектура Mini App, компоненты и страницы | ✅ Actual |
| [03_Frontend/Config.md](03_Frontend/Config.md) | Конфигурация фронтенда и связь с API | ✅ Actual |
| [04_DevOps/LocalSetup.md](04_DevOps/LocalSetup.md) | Руководство по локальному запуску проекта | ✅ Actual |
| [04_DevOps/Deploy.md](04_DevOps/Deploy.md) | Инструкции по деплою и управлению сервером | ✅ Actual |
| [04_DevOps/Secrets.md](04_DevOps/Secrets.md) | Переменные окружения и безопасность | ✅ Actual |
| [99_State/Changelog.md](99_State/Changelog.md) | Журнал изменений проекта | ✅ Actual |
| [99_State/Issues.md](99_State/Issues.md) | Известные проблемы, баги и техдолг | 🚨 Critical |
| [99_State/ArchitectureReview.md](99_State/ArchitectureReview.md) | Ревью архитектуры: сильные стороны, проблемы, рекомендации | ✅ Actual |

---

## 🛠 Правила обновления (для AI и разработчиков)

Документация должна обновляться **синхронно** с изменениями в коде:
1. **Изменил эндпоинт** → обнови `02_Backend/API.md` и дату в `INDEX.md`.
2. **Изменил модель БД** → обнови `01_System/DataModel.md`.
3. **Пофиксил баг** → обнови `99_State/Issues.md` и `99_State/Changelog.md`.
4. **Создал новый документ** → добавь строку в таблицу выше.

Все файлы документации (кроме этого) используют YAML-метаданные согласно скиллу `docs-metadata`.
