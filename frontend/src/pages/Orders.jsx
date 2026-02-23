import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import StatusBadge from '../components/ui/StatusBadge'
import OrderProgress from '../components/ui/OrderProgress'

const FILTERS = [
  { id: 'all', label: 'Все' },
  { id: 'new', label: 'Новые' },
  { id: 'in_progress', label: 'В работе' },
  { id: 'done', label: 'Выполнены' },
  { id: 'canceled', label: 'Отменены' },
]

// Mock данные — заменить на GET /api/requests
const MOCK_ORDERS = [
  {
    id: 'ORD-003',
    title: 'Курсовая по экономическому анализу',
    status: 'in_progress',
    date: '20 февраля 2026',
    deadline: '5 марта 2026',
    price: '3 500 ₽',
    icon: '📊',
    subject: 'Экономический анализ',
    currentStep: 2,
  },
  {
    id: 'ORD-002',
    title: 'Лабораторная работа по программированию',
    status: 'done',
    date: '10 февраля 2026',
    deadline: '15 февраля 2026',
    price: '1 800 ₽',
    icon: '💻',
    subject: 'Программирование',
    currentStep: 3,
  },
  {
    id: 'ORD-001',
    title: 'Реферат по менеджменту',
    status: 'done',
    date: '1 февраля 2026',
    deadline: '7 февраля 2026',
    price: '900 ₽',
    icon: '📄',
    subject: 'Менеджмент',
    currentStep: 3,
  },
]

export default function Orders() {
  const [activeFilter, setActiveFilter] = useState('all')
  const navigate = useNavigate()

  const filtered =
    activeFilter === 'all'
      ? MOCK_ORDERS
      : MOCK_ORDERS.filter((o) => o.status === activeFilter)

  return (
    <div className="orders-page">
      <div className="orders-page__container">
        {/* Фильтры */}
        <div className="orders-filters">
          {FILTERS.map((f) => (
            <button
              key={f.id}
              className={`filter-chip${activeFilter === f.id ? ' active' : ''}`}
              onClick={() => setActiveFilter(f.id)}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Список */}
        {filtered.length === 0 ? (
          <div className="orders-empty">
            <div className="orders-empty__icon">📭</div>
            <h2 className="orders-empty__title">Заявок нет</h2>
            <p className="orders-empty__sub">
              В этой категории пока нет заявок. Оформите первую!
            </p>
            <button
              className="btn btn--primary"
              style={{ marginTop: 8 }}
              onClick={() => navigate('/new-order')}
            >
              📝 Новая заявка
            </button>
          </div>
        ) : (
          filtered.map((order) => (
            <div
              key={order.id}
              className="order-card"
              onClick={() => navigate(`/orders/${order.id}`)}
            >
              <div className="order-card__header">
                <span className="order-card__id">#{order.id}</span>
                <StatusBadge status={order.status} />
              </div>

              <h3 className="order-card__title">
                {order.icon} {order.title}
              </h3>

              <div className="order-card__meta">
                <span className="order-card__meta-item">📅 {order.date}</span>
                <span className="order-card__meta-item">
                  ⏰ Дедлайн: {order.deadline}
                </span>
              </div>

              {order.status === 'in_progress' && (
                <div className="order-card__progress">
                  <OrderProgress currentStep={order.currentStep} />
                </div>
              )}

              <div className="order-card__footer">
                <span className="order-card__price">
                  {order.price} <span>к оплате</span>
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: 20 }}>›</span>
              </div>
            </div>
          ))
        )}

        {filtered.length > 0 && (
          <button
            className="btn btn--green"
            onClick={() => navigate('/new-order')}
          >
            📝 Оформить новую заявку
          </button>
        )}
      </div>
    </div>
  )
}
