import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import StatusBadge from '../components/ui/StatusBadge'
import OrderProgress from '../components/ui/OrderProgress'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL, getApiHeaders } from '../config'

/** Форматирование обратного отсчёта из ISO-даты */
function useCountdown(deadline) {
  const [timeLeft, setTimeLeft] = useState('')

  useEffect(() => {
    if (!deadline) return
    function tick() {
      const diff = new Date(deadline) - Date.now()
      if (diff <= 0) { setTimeLeft('Истекло'); return }
      const h = Math.floor(diff / 3600000)
      const m = Math.floor((diff % 3600000) / 60000)
      setTimeLeft(h > 0 ? `${h}ч ${m}мин` : `${m}мин`)
    }
    tick()
    const id = setInterval(tick, 30000)
    return () => clearInterval(id)
  }, [deadline])

  return timeLeft
}

export default function OrderDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, haptic, initData } = useTelegram()
  const [order, setOrder] = useState(null)
  const [payment, setPayment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [bonusInput, setBonusInput] = useState(0)
  const [userProfile, setUserProfile] = useState(null)
  const [disputeReason, setDisputeReason] = useState('')
  const [showDispute, setShowDispute] = useState(false)

  const userId = user?.id

  // Загрузка заказа + платежа + профиля
  const fetchData = useCallback(async () => {
    try {
      const headers = getApiHeaders(initData)
      const [orderRes, payRes, profileRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/orders/${id}`, { headers }),
        fetch(`${API_BASE_URL}/api/payments/order/${id}`, { headers }),
        userId ? fetch(`${API_BASE_URL}/api/users/${userId}`, { headers }) : null,
      ])

      if (orderRes.ok) setOrder(await orderRes.json())
      if (payRes.ok) {
        const payments = await payRes.json()
        // Берём последний актуальный платёж (paid или pending)
        const active = payments.find(p => p.status === 'paid') || payments.find(p => p.status === 'pending') || payments[0]
        setPayment(active || null)
      }
      if (profileRes?.ok) setUserProfile(await profileRes.json())
    } catch (err) {
      console.error('Fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [id, initData, userId])

  useEffect(() => { fetchData() }, [fetchData])

  // Обратный отсчёт
  const paymentDeadline = useCountdown(order?.payment_deadline)
  const cancelDeadline = useCountdown(payment?.cancel_deadline)

  // --- Действия ---

  async function handlePay() {
    haptic('impact', 'medium')
    setActionLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/payments/create`, {
        method: 'POST',
        headers: { ...getApiHeaders(initData), 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_id: Number(id),
          user_id: userId,
          bonus_amount: bonusInput,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ошибка оплаты')

      if (data.confirmation_url) {
        // Переход на страницу провайдера
        window.location.href = data.confirmation_url
      } else {
        // Оплачено бонусами — обновляем данные
        haptic('notification', 'success')
        await fetchData()
      }
    } catch (err) {
      haptic('notification', 'error')
      alert(err.message)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleCancelPayment() {
    if (!payment) return
    if (!window.confirm('Отменить оплату? Средства вернутся на карту.')) return
    haptic('notification', 'warning')
    setActionLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/payments/${payment.id}/cancel`, {
        method: 'POST',
        headers: { ...getApiHeaders(initData), 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ошибка отмены')
      haptic('notification', 'success')
      await fetchData()
    } catch (err) {
      haptic('notification', 'error')
      alert(err.message)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleCancelOrder() {
    if (!window.confirm('Вы уверены, что хотите отменить эту заявку?')) return
    haptic('notification', 'warning')
    setActionLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/orders/${id}/cancel`, {
        method: 'POST',
        headers: getApiHeaders(initData),
      })
      if (res.ok) {
        navigate('/orders')
      } else {
        throw new Error('Ошибка отмены')
      }
    } catch (err) {
      alert('Ошибка при отмене заявки')
    } finally {
      setActionLoading(false)
    }
  }

  async function handleConfirm() {
    if (!window.confirm('Подтвердить выполнение работы?')) return
    haptic('impact', 'medium')
    setActionLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/orders/${id}/confirm`, {
        method: 'POST',
        headers: { ...getApiHeaders(initData), 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ошибка подтверждения')
      haptic('notification', 'success')
      await fetchData()
    } catch (err) {
      haptic('notification', 'error')
      alert(err.message)
    } finally {
      setActionLoading(false)
    }
  }

  async function handleDispute() {
    if (!disputeReason.trim()) return alert('Укажите причину спора')
    haptic('notification', 'warning')
    setActionLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/api/orders/${id}/dispute`, {
        method: 'POST',
        headers: { ...getApiHeaders(initData), 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, reason: disputeReason }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ошибка')
      haptic('notification', 'success')
      setShowDispute(false)
      setDisputeReason('')
      await fetchData()
    } catch (err) {
      haptic('notification', 'error')
      alert(err.message)
    } finally {
      setActionLoading(false)
    }
  }

  // --- Рендер ---

  if (loading) return <div className="order-detail"><p style={{textAlign: 'center', marginTop: 50}}>Загрузка...</p></div>
  if (!order) return <div className="order-detail"><p style={{textAlign: 'center', marginTop: 50}}>Заявка не найдена</p></div>

  const getWorkIcon = (type) => {
    const icons = { coursework: '📊', diploma: '🎓', abstract: '📄', lab: '🔬', practice: '🏢' }
    return icons[type] || '📌'
  }

  const getWorkLabel = (type) => {
    const labels = { coursework: 'Курсовая', diploma: 'Диплом', abstract: 'Реферат', lab: 'Лабораторная', practice: 'Практика' }
    return labels[type] || 'Другое'
  }

  const getFullFileUrl = (path) => {
    if (path.startsWith('http')) return path
    return `${API_BASE_URL}${path}`
  }

  const maxBonus = userProfile?.bonus_balance
    ? Math.min(userProfile.bonus_balance, order.price ? order.price * 0.5 : 0)
    : 0

  const canCancelPayment = payment?.status === 'paid' && payment?.cancel_deadline && new Date(payment.cancel_deadline) > Date.now()

  return (
    <div className="order-detail">
      <div className="order-detail__container">
        {/* Hero */}
        <div className="order-detail__hero">
          <p className="order-detail__number">Заявка #{order.id}</p>
          <h1 className="order-detail__title">
            {getWorkIcon(order.work_type)} {order.subject}
          </h1>
          <StatusBadge status={order.status} />
        </div>

        {/* Прогресс */}
        <OrderProgress status={order.status} />

        {/* Детали */}
        <div className="detail-list">
          <div className="detail-row">
            <span className="detail-row__label">Тип работы</span>
            <span className="detail-row__value">{getWorkLabel(order.work_type)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-row__label">Тема</span>
            <span className="detail-row__value">{order.topic}</span>
          </div>
          {order.teacher && (
            <div className="detail-row">
              <span className="detail-row__label">Преподаватель</span>
              <span className="detail-row__value">{order.teacher}</span>
            </div>
          )}
          {order.deadline && (
            <div className="detail-row">
              <span className="detail-row__label">Дедлайн</span>
              <span className="detail-row__value">{new Date(order.deadline).toLocaleDateString()}</span>
            </div>
          )}
          {order.antiplagiat_percent && (
            <div className="detail-row">
              <span className="detail-row__label">Антиплагиат</span>
              <span className="detail-row__value">≥ {order.antiplagiat_percent}%</span>
            </div>
          )}
          <div className="detail-row">
            <span className="detail-row__label">Стоимость</span>
            <span className="detail-row__value" style={{ color: 'var(--accent)', fontWeight: 800 }}>
              {order.price ? `${order.price} ₽` : 'По договорённости'}
            </span>
          </div>
        </div>

        {/* ========== БЛОК ОПЛАТЫ — priced ========== */}
        {order.status === 'priced' && order.price > 0 && (
          <div className="payment-block">
            <div className="payment-block__header">
              <h3 className="payment-block__title">Оплата заказа</h3>
              {paymentDeadline && (
                <span className="payment-block__deadline">
                  {paymentDeadline === 'Истекло' ? '⏰ Время истекло' : `⏳ ${paymentDeadline}`}
                </span>
              )}
            </div>

            <div className="payment-block__summary">
              <div className="payment-block__row">
                <span>Стоимость работы</span>
                <span className="payment-block__amount">{order.price} ₽</span>
              </div>
              {bonusInput > 0 && (
                <div className="payment-block__row payment-block__row--bonus">
                  <span>Бонусы</span>
                  <span>−{bonusInput} ₽</span>
                </div>
              )}
              <div className="payment-block__row payment-block__row--total">
                <span>К оплате</span>
                <span>{Math.max(0, order.price - bonusInput)} ₽</span>
              </div>
            </div>

            {/* Бонусы */}
            {maxBonus > 0 && (
              <div className="payment-block__bonus">
                <div className="payment-block__bonus-header">
                  <span>Использовать бонусы</span>
                  <span className="payment-block__bonus-balance">
                    Доступно: {userProfile.bonus_balance} ₽
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={maxBonus}
                  step={1}
                  value={bonusInput}
                  onChange={(e) => setBonusInput(Number(e.target.value))}
                  className="payment-block__slider"
                />
                <div className="payment-block__bonus-value">{bonusInput} ₽</div>
              </div>
            )}

            <button
              className="btn btn--green payment-block__btn"
              onClick={handlePay}
              disabled={actionLoading || paymentDeadline === 'Истекло'}
            >
              {actionLoading ? '⏳ Обработка...' : `Оплатить ${Math.max(0, order.price - bonusInput)} ₽`}
            </button>
          </div>
        )}

        {/* ========== БЛОК ПОСЛЕ ОПЛАТЫ — paid ========== */}
        {order.status === 'paid' && payment && (
          <div className="payment-block payment-block--paid">
            <div className="payment-block__header">
              <h3 className="payment-block__title">Оплата прошла</h3>
              <span className="payment-block__check">✓</span>
            </div>
            <div className="payment-block__summary">
              <div className="payment-block__row">
                <span>Оплачено</span>
                <span className="payment-block__amount">{payment.amount} ₽</span>
              </div>
              {payment.bonus_used > 0 && (
                <div className="payment-block__row payment-block__row--bonus">
                  <span>Использовано бонусов</span>
                  <span>{payment.bonus_used} ₽</span>
                </div>
              )}
            </div>

            {canCancelPayment && (
              <div className="payment-block__cancel-zone">
                <p className="payment-block__cancel-hint">
                  Отмена доступна ещё {cancelDeadline}
                </p>
                <button
                  className="btn btn--outline payment-block__btn"
                  onClick={handleCancelPayment}
                  disabled={actionLoading}
                  style={{ color: '#f44336', borderColor: '#f44336' }}
                >
                  {actionLoading ? '⏳ Отмена...' : 'Отменить оплату'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* ========== ПОДТВЕРЖДЕНИЕ — confirming / done ========== */}
        {(order.status === 'confirming' || order.status === 'done') && (
          <div className="payment-block payment-block--confirm">
            <div className="payment-block__header">
              <h3 className="payment-block__title">Работа выполнена</h3>
            </div>
            <p className="payment-block__desc">
              Проверьте работу и подтвердите, что всё в порядке. Если есть проблемы — откройте спор.
            </p>

            <div className="payment-block__actions">
              <button
                className="btn btn--green payment-block__btn"
                onClick={handleConfirm}
                disabled={actionLoading}
              >
                {actionLoading ? '⏳ ...' : '✓ Подтвердить работу'}
              </button>

              {!showDispute ? (
                <button
                  className="btn btn--ghost payment-block__btn"
                  onClick={() => setShowDispute(true)}
                  style={{ color: '#f44336' }}
                >
                  Открыть спор
                </button>
              ) : (
                <div className="payment-block__dispute">
                  <textarea
                    className="payment-block__textarea"
                    placeholder="Опишите проблему..."
                    value={disputeReason}
                    onChange={(e) => setDisputeReason(e.target.value)}
                    rows={3}
                  />
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button
                      className="btn btn--outline payment-block__btn"
                      onClick={handleDispute}
                      disabled={actionLoading}
                      style={{ flex: 1, color: '#f44336', borderColor: '#f44336' }}
                    >
                      Отправить
                    </button>
                    <button
                      className="btn btn--ghost payment-block__btn"
                      onClick={() => { setShowDispute(false); setDisputeReason('') }}
                      style={{ flex: 1 }}
                    >
                      Отмена
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========== COMPLETED ========== */}
        {order.status === 'completed' && (
          <div className="payment-block payment-block--completed">
            <div className="payment-block__header">
              <h3 className="payment-block__title">Заказ завершён</h3>
              <span className="payment-block__check">🎉</span>
            </div>
            <p className="payment-block__desc">
              Работа принята. Спасибо за использование сервиса!
            </p>
          </div>
        )}

        {/* ========== DISPUTED ========== */}
        {order.status === 'disputed' && (
          <div className="payment-block payment-block--disputed">
            <div className="payment-block__header">
              <h3 className="payment-block__title">Спор открыт</h3>
              <span className="payment-block__check">⚠️</span>
            </div>
            <p className="payment-block__desc">
              Ваше обращение рассматривается администратором. Мы свяжемся с вами в ближайшее время.
            </p>
          </div>
        )}

        {/* ПРИКРЕПЛЕННЫЕ ФАЙЛЫ */}
        {order.attachments && order.attachments.length > 0 && (
          <div className="form-card" style={{ gap: 10 }}>
            <h3 className="form-card__title" style={{fontSize: 16}}>📎 Прикрепленные документы</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {order.attachments.map((file, index) => (
                <a
                  key={index}
                  href={getFullFileUrl(file)}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '10px 12px',
                    background: 'var(--bg-secondary)',
                    borderRadius: 8,
                    textDecoration: 'none',
                    color: 'var(--text-primary)',
                    fontSize: 14
                  }}
                >
                  <span>📄</span>
                  <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    Документ #{index + 1}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--accent)' }}>Скачать ›</span>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Требования */}
        {order.requirements && (
          <div className="form-card" style={{ gap: 8 }}>
            <h3 className="form-card__title">Требования</h3>
            <p style={{ fontSize: 'var(--font-size-md)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {order.requirements}
            </p>
          </div>
        )}

        <div style={{marginTop: 10, display: 'flex', flexDirection: 'column', gap: 12}}>
          {order.status === 'new' && (
            <button
              className="btn btn--danger"
              onClick={handleCancelOrder}
              disabled={actionLoading}
              style={{backgroundColor: '#ff4d4f', color: 'white'}}
            >
              {actionLoading ? '⏳ Отмена...' : '❌ Отменить заявку'}
            </button>
          )}

          <button
            className="btn btn--ghost"
            onClick={() => navigate(-1)}
          >
            ← Назад к списку
          </button>
        </div>
      </div>
    </div>
  )
}
