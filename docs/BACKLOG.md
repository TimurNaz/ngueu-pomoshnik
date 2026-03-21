# Бэклог проекта НГУЭУ/Помощник

Собрано из аудита кода, логов и инфраструктуры (2026-03-22).

---

## P0 — Критично (безопасность)

### SEC-01: API без аутентификации
Любой знающий `user_id` может создавать заказы, читать профиль и историю от чужого имени.
**Решение**: Валидация `initData` от Telegram WebApp на бэкенде. Telegram подписывает данные HMAC — проверять подпись на каждый запрос.

### SEC-02: Хардкод fallback userId
`const userId = user?.id || 927125510` в `NewOrder.jsx` — если Telegram SDK не загрузится, заказ создаётся от имени админа.
**Решение**: Убрать fallback, показывать ошибку если userId не получен.

### SEC-03: Слабый пароль БД
`DB_PASSWORD='2005'` — легко угадать.
**Решение**: Сгенерировать криптостойкий пароль (32+ символов).

### SEC-04: CORS allow_origins=["*"]
Любой сайт может слать запросы к API.
**Решение**: Ограничить до домена Mini App (`olddiamond.online` или актуальный).

### SEC-05: Дефолтная БД `postgres`
`DB_NAME=postgres` — используется системная БД вместо отдельной.
**Решение**: Создать отдельную БД `ngueu_db`, обновить `.env`.

---

## P1 — Важно (стабильность)

### INFRA-01: Нет бэкапов БД
При потере Docker volume все данные пропадут безвозвратно.
**Решение**: Cron-задача `pg_dump` + хранение в S3/облаке.

### INFRA-02: Нет мониторинга ошибок
Ошибки видны только в `docker compose logs`.
**Решение**: Подключить Sentry (бесплатный тариф для стартапов).

### INFRA-03: Unclosed aiohttp client session
При остановке API в логах: `ERROR:asyncio:Unclosed client session`.
**Решение**: Закрывать сессию в `@app.on_event("shutdown")`.

### INFRA-04: Бот теряет связь с Telegram на часы
На Яндекс Облаке бот не мог подключиться к `api.telegram.org` по 3+ часа (189 попыток подряд). РКН блокирует IP Telegram.
**Решение**: Использовать прокси/VPN для подключения к Telegram API, или хостинг за пределами РФ.

### INFRA-05: Нет CI/CD
Деплой ручной через `deploy.sh`.
**Решение**: GitHub Actions: линтер + тесты + деплой по push в main.

---

## P2 — Улучшения (качество)

### CODE-01: Нет тестов
Ни unit, ни integration тестов.
**Решение**: Начать с API-эндпоинтов (pytest + httpx), покрыть критичные сценарии: создание заказа, регистрация.

### CODE-02: Urgency мисматч frontend/backend
Frontend шлёт `3d`/`1w`/`2w`/`1m`, БД Enum ждёт `three_days`/`one_week`/`two_weeks`/`one_month`. Есть маппинг в API, но это хрупко.
**Решение**: Привести к единому формату — либо frontend шлёт Enum-значения, либо БД принимает короткие.

### CODE-03: redis.py закомментирован
`redis.py` — весь закомментирован, бот использует MemoryStorage (теряет состояние при перезапуске).
**Решение**: Подключить Redis или удалить файл если не планируется.

---

## P3 — Защита от сканеров (nginx)

### SEC-06: Nginx отдаёт 200 на любой путь
WordPress-сканеры получают 200 на `/xmlrpc.php`, `/wp-admin/` и т.д., что провоцирует дальнейшие атаки.
**Решение**:
```nginx
location ~* ^/(wp-|xmlrpc|\.env|\.git|phpmyadmin|admin|cgi-bin) {
    return 444;
}
```

### SEC-07: Нет rate limiting
API можно спамить без ограничений.
**Решение**:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

### SEC-08: Нет security-заголовков
**Решение**:
```nginx
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header Referrer-Policy strict-origin-when-cross-origin;
```
