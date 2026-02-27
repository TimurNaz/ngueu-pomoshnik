#!/usr/bin/env bash

# --- КОНФИГУРАЦИЯ ---
SERVER_IP="158.160.202.185"
SERVER_USER="ubuntu"
PROJECT_PATH="/app/ngueu-pomoshnik"
BRANCH=$(git branch --show-current)

echo "🚀 Начинаю деплой ветки [$BRANCH] на сервер $SERVER_IP..."

# 1. Сохраняем и пушим код
echo "📦 Шаг 1: Пуш кода в GitLab..."
git add .
read -p "Введите сообщение коммита: " message
if [ -z "$message" ]; then
  message="Auto-deploy $(date +'%Y-%m-%d %H:%M:%S')"
fi
git commit -m "$message"
git push origin $BRANCH

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при пуше в GitLab. Деплой прерван."
    exit 1
fi

# 2. Обновляем сервер по SSH
echo "🌐 Шаг 2: Обновление сервера..."
ssh -t $SERVER_USER@$SERVER_IP "
    cd $PROJECT_PATH && 
    git fetch origin && 
    git checkout $BRANCH && 
    git pull origin $BRANCH && 
    docker-compose up -d --build
"

if [ $? -eq 0 ]; then
    echo "✅ ДЕПЛОЙ УСПЕШНО ЗАВЕРШЕН!"
    echo "Бот и API работают 24/7 по адресу сервера."
else
    echo "❌ Произошла ошибка при обновлении сервера."
fi
