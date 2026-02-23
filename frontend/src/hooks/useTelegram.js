/**
 * useTelegram — хук для работы с Telegram WebApp API.
 * Безопасно возвращает заглушки для разработки в браузере.
 */
export function useTelegram() {
  const tg = window.Telegram?.WebApp

  const user = tg?.initDataUnsafe?.user ?? {
    id: 123456789,
    first_name: 'Студент',
    last_name: 'НГУЭУ',
    username: 'student_ngueu',
  }

  function close() {
    tg?.close()
  }

  function ready() {
    tg?.ready()
  }

  function expand() {
    tg?.expand()
  }

  function haptic(type = 'impact', style = 'light') {
    tg?.HapticFeedback?.[type]?.(style)
  }

  return {
    tg,
    user,
    close,
    ready,
    expand,
    haptic,
    colorScheme: tg?.colorScheme ?? 'light',
    isExpanded: tg?.isExpanded ?? false,
  }
}
