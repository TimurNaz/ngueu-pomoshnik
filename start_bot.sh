#!/usr/bin/env bash

# Устанавливаем PYTHONPATH, чтобы Python видел пакеты из backend/bot
export PYTHONPATH="$(pwd)/backend/bot"

# Запуск бота
python backend/bot/main.py
