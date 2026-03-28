import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL, getApiHeaders } from '../config'

const TYPE_ICONS = {
  order_created: '📝',
  executor_assigned: '👤',
  order_in_progress: '⚙️',
  order_review: '👀',
  order_done: '✅',
  order_canceled: '❌',
  bonus: '🎁',
  system: '⚙️',
  price_set: '💰',
  payment_success: '💳',
  payment_refunded: '↩️',
  payment_reminder: '⏰',
  order_completed: '🎉',
  order_confirming: '📋',
  order_disputed: '⚠️',
  confirmation_reminder: '🔔',
}

const TYPE_COLORS = {
  order_created: 'blue',
  executor_assigned: 'accent',
  order_in_progress: 'accent',
  order_review: 'yellow',
  order_done: 'green',
  order_canceled: 'red',
  bonus: 'yellow',
  system: 'neutral',
  price_set: 'yellow',
  payment_success: 'green',
  payment_refunded: 'red',
  payment_reminder: 'yellow',
  order_completed: 'green',
  order_confirming: 'accent',
  order_disputed: 'red',
  confirmation_reminder: 'yellow',
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'только что'
  if (mins < 60) return `${mins} мин назад`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} ч назад`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} дн назад`
  return new Date(dateStr).toLocaleDateString()
}

export default function Notifications() {
  const navigate = useNavigate()
  const { user, haptic } = useTelegram()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  const userId = user?.id
  const initData = window.Telegram?.WebApp?.initData || ''

  useEffect(() => {
    if (!userId) return
    fetchNotifications()
  }, [userId])

  async function fetchNotifications() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/notifications/${userId}`, {
        headers: getApiHeaders(initData),
      })
      if (res.ok) {
        const data = await res.json()
        setNotifications(data)
      }
    } catch (err) {
      console.error('Ошибка загрузки уведомлений:', err)
    } finally {
      setLoading(false)
    }
  }

  const unreadCount = notifications.filter(n => !n.read).length

  async function handleClick(notif) {
    haptic('impact', 'light')
    // Помечаем как прочитанное
    if (!notif.read) {
      try {
        await fetch(`${API_BASE_URL}/api/notifications/${notif.id}/read?user_id=${userId}`, {
          method: 'POST',
          headers: getApiHeaders(initData),
        })
        setNotifications(prev =>
          prev.map(n => n.id === notif.id ? { ...n, read: true } : n)
        )
      } catch (err) {
        console.error('Ошибка при пометке прочитанным:', err)
      }
    }
    // Переход к заявке если есть
    if (notif.order_id) {
      navigate(`/orders/${notif.order_id}`)
    }
  }

  async function markAllRead() {
    haptic('notification', 'success')
    try {
      await fetch(`${API_BASE_URL}/api/notifications/${userId}/read-all`, {
        method: 'POST',
        headers: getApiHeaders(initData),
      })
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    } catch (err) {
      console.error('Ошибка при пометке всех прочитанными:', err)
    }
  }

  if (loading) {
    return (
      <div className="notifications-page">
        <div className="notifications-page__container">
          <div className="notifications-header">
            <h1 className="notifications-header__title">Уведомления</h1>
          </div>
          <div className="notifications-empty">
            <p className="notifications-empty__icon">⏳</p>
            <p className="notifications-empty__title">Загрузка...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="notifications-page">
      <div className="notifications-page__container">
        {/* Заголовок */}
        <div className="notifications-header">
          <div>
            <h1 className="notifications-header__title">Уведомления</h1>
            {unreadCount > 0 && (
              <p className="notifications-header__count">{unreadCount} непрочитанных</p>
            )}
          </div>
          {unreadCount > 0 && (
            <button className="notifications-header__mark-all" onClick={markAllRead}>
              Прочитать все
            </button>
          )}
        </div>

        {/* Список */}
        {notifications.length === 0 ? (
          <div className="notifications-empty">
            <p className="notifications-empty__icon">🔔</p>
            <p className="notifications-empty__title">Нет уведомлений</p>
            <p className="notifications-empty__sub">Здесь появятся обновления по вашим заявкам</p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map(notif => (
              <div
                key={notif.id}
                className={`notification-card ${!notif.read ? 'notification-card--unread' : ''}`}
                onClick={() => handleClick(notif)}
              >
                <div className={`notification-card__icon notification-card__icon--${TYPE_COLORS[notif.type] || 'neutral'}`}>
                  {TYPE_ICONS[notif.type] || '📌'}
                </div>
                <div className="notification-card__content">
                  <div className="notification-card__top">
                    <p className="notification-card__title">{notif.title}</p>
                    <span className="notification-card__time">{timeAgo(notif.created_at)}</span>
                  </div>
                  <p className="notification-card__text">{notif.text}</p>
                </div>
                {!notif.read && <div className="notification-card__dot" />}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
