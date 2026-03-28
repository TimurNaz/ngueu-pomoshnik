import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL, getApiHeaders } from '../config'

export default function Header() {
  const { user, haptic } = useTelegram()
  const navigate = useNavigate()
  const [unreadCount, setUnreadCount] = useState(0)

  const userId = user?.id
  const initData = window.Telegram?.WebApp?.initData || ''

  useEffect(() => {
    if (!userId) return
    fetchUnreadCount()
    // Обновляем каждые 30 секунд
    const interval = setInterval(fetchUnreadCount, 30000)
    return () => clearInterval(interval)
  }, [userId])

  async function fetchUnreadCount() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/notifications/${userId}/unread-count`, {
        headers: getApiHeaders(initData),
      })
      if (res.ok) {
        const data = await res.json()
        setUnreadCount(data.count)
      }
    } catch {
      // Молча игнорируем — бейдж просто не обновится
    }
  }

  function handleBellClick() {
    haptic('impact', 'light')
    navigate('/notifications')
  }

  return (
    <header className="header">
      <div className="header__inner">
        <div className="header__logo">
          <img src="/images/logo.png" alt="nG" className="header__logo-icon" />
          <div className="header__logo-text">
            <span className="header__title">НГУЭУ/Помощник</span>
            <span className="header__subtitle">Учебные работы</span>
          </div>
        </div>
        <button
          className="header__action"
          onClick={handleBellClick}
          aria-label="Уведомления"
        >
          🔔
          {unreadCount > 0 && (
            <span className="header__badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
          )}
        </button>
      </div>
    </header>
  )
}
