import { useParams, useNavigate } from 'react-router-dom'
import StatusBadge from '../components/ui/StatusBadge'
import OrderProgress from '../components/ui/OrderProgress'
import { useTelegram } from '../hooks/useTelegram'

// Mock — заменить на GET /api/requests/:id
const MOCK_ORDER = {
  id: 'ORD-003',
  title: 'Курсовая по экономическому анализу',
  status: 'in_progress',
  subject: 'Экономический анализ',
  topic: 'Анализ финансовой устойчивости предприятия',
  teacher: 'Иванова Н.В.',
  workType: 'Курсовая работа',
  deadline: '5 марта 2026',
  urgency: '2 недели',
  antiplagiat: '≥ 75%',
  requirements: 'Объём 40-50 страниц, ГОСТ 7.1-2003, 30+ источников.',
  price: '3 500 ₽',
  icon: '📊',
  currentStep: 2,
  executor: {
    name: 'Исполнитель #12',
    rating: 4.9,
    count: 47,
    spec: 'Экономика, финансы',
  },
}

export default function OrderDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { haptic } = useTelegram()

  // TODO: запрос GET /api/requests/${id}
  const order = MOCK_ORDER

  function handlePay() {
    haptic('notification', 'success')
    // TODO: открыть платёжную страницу ЮKassa
    alert('Переход к оплате (ЮKassa)')
  }

  function handleAccept() {
    haptic('notification', 'success')
    alert('Работа принята!')
  }

  return (
    <div className="order-detail">
      <div className="order-detail__container">
        {/* Hero */}
        <div className="order-detail__hero">
          <p className="order-detail__number">Заявка #{order.id}</p>
          <h1 className="order-detail__title">
            {order.icon} {order.title}
          </h1>
          <StatusBadge status={order.status} />
        </div>

        {/* Прогресс */}
        <OrderProgress currentStep={order.currentStep} />

        {/* Исполнитель */}
        {order.executor && (
          <div className="executor-card">
            <div className="executor-card__avatar">👤</div>
            <div className="executor-card__info">
              <p className="executor-card__name">{order.executor.name}</p>
              <div className="executor-card__rating">
                <span className="executor-card__rating-stars">★★★★★</span>
                {order.executor.rating} · {order.executor.count} работ
              </div>
            </div>
            <span className="executor-card__badge">
              {order.executor.spec}
            </span>
          </div>
        )}

        {/* Детали */}
        <div className="detail-list">
          <div className="detail-row">
            <span className="detail-row__label">Тип работы</span>
            <span className="detail-row__value">{order.workType}</span>
          </div>
          <div className="detail-row">
            <span className="detail-row__label">Дисциплина</span>
            <span className="detail-row__value">{order.subject}</span>
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
          <div className="detail-row">
            <span className="detail-row__label">Дедлайн</span>
            <span className="detail-row__value">{order.deadline}</span>
          </div>
          {order.antiplagiat !== 'Не требуется' && (
            <div className="detail-row">
              <span className="detail-row__label">Антиплагиат</span>
              <span className="detail-row__value">{order.antiplagiat}</span>
            </div>
          )}
          <div className="detail-row">
            <span className="detail-row__label">Стоимость</span>
            <span className="detail-row__value" style={{ color: 'var(--accent)', fontWeight: 800 }}>
              {order.price}
            </span>
          </div>
        </div>

        {/* Требования */}
        {order.requirements && (
          <div className="form-card" style={{ gap: 8 }}>
            <h3 className="form-card__title">Требования</h3>
            <p style={{ fontSize: 'var(--font-size-md)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {order.requirements}
            </p>
          </div>
        )}

        {/* Действия */}
        {order.status === 'in_progress' && order.currentStep === 1 && (
          <button className="btn btn--green" onClick={handlePay}>
            💳 Оплатить и подтвердить
          </button>
        )}

        {order.status === 'in_progress' && order.currentStep === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <button className="btn btn--green" onClick={handleAccept}>
              ✅ Принять работу
            </button>
            <button className="btn btn--ghost">
              ✏️ Запросить правки
            </button>
          </div>
        )}

        <button
          className="btn btn--ghost"
          onClick={() => navigate(-1)}
        >
          ← Назад к списку
        </button>
      </div>
    </div>
  )
}
