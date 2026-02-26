# Используем легкий и быстрый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости, нужные для PostgreSQL и сборки
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бэкенда
COPY backend/ ./backend/

# Добавляем backend/bot в PYTHONPATH, чтобы импорты работали корректно
ENV PYTHONPATH=/app/backend/bot

# Команда по умолчанию (будет переопределяться в docker-compose)
CMD ["python", "backend/bot/main.py"]
