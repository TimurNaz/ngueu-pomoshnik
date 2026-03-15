/**
 * Глобальная конфигурация API
 */

// Базовый URL бэкенда.
// Используем текущий домен, так как Nginx проксирует запросы /api на бэкенд
export const API_BASE_URL = window.location.origin;

/**
 * Вспомогательная функция для генерации заголовков запроса.
 * Добавляет авторизацию Telegram и необходимые технические заголовки.
 * @param {string} initData - Сырые данные из Telegram.WebApp.initData
 * @param {Object} extraHeaders - Дополнительные заголовки
 */
export const getApiHeaders = (initData = '', extraHeaders = {}) => {
  return {
    'bypass-tunnel-reminder': 'true',
    'X-TG-Init-Data': initData,
    ...extraHeaders
  };
};
