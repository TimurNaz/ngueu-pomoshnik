/**
 * Инициализация Telegram Web App (Mini App).
 * Вызывается при старте приложения в main.jsx.
 */
export function initTelegramWebApp() {
  const tg = window.Telegram?.WebApp
  if (tg) {
    tg.ready()
    tg.expand()
  }
}

/**
 * Хук для доступа к Telegram Web App API в компонентах.
 * @returns {object|undefined} tg WebApp или undefined вне Telegram
 */
export function useTelegram() {
  return window.Telegram?.WebApp
}
