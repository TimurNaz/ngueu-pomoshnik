# Этап 1: Сборка
FROM node:18-alpine AS builder

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package.json package-lock.json* ./
RUN npm install

# Копируем остальной код и собираем проект
COPY . .
RUN npm run build

# Этап 2: Раздача через Nginx
FROM nginx:alpine

# Удаляем дефолтный конфиг Nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем собранные файлы из первого этапа
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем наш кастомный конфиг (мы создадим его следующим шагом)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
