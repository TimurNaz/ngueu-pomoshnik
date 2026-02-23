import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import StatusBadge from '../components/ui/StatusBadge'

// Mock данные для демонстрации — заменить на API-запросы
const MOCK_ORDERS = [
  {
    id: 'ORD-001',
    title: 'Курсовая по экономике',
    status: 'in_progress',
    date: '20 фев',
    price: '3 500 ₽',
    icon: '📊',
  },
  {
    id: 'ORD-002',
    title: 'Лабораторная по ИТ',
    status: 'done',
    date: '15 фев',
    price: '1 800 ₽',
    icon: '💻',
  },
]

export default function Home() {
  const navigate = useNavigate()
  const { user, haptic } = useTelegram()

  const displayName = user?.first_name ?? 'Студент'

  function handleAction(path) {
    haptic('impact', 'light')
    navigate(path)
  }

  return (
    <div className="home">
      <div className="home__container">
        {/* Приветствие */}
        <div className="greeting">
          <div className="greeting__info">
            <p className="greeting__sup">Добро пожаловать 👋</p>
            <h1 className="greeting__title">{displayName}</h1>
          </div>
          <div className="greeting__avatar">
            {displayName[0]?.toUpperCase() ?? '👤'}
          </div>
        </div>

        {/* Бонусная карта */}
        <div className="bonus-card">
          <div className="bonus-card__header">
            <div>
              <p className="bonus-card__label">Бонусные баллы</p>
              <p className="bonus-card__brand">НГУЭУ/Помощник</p>
            </div>
            <span className="bonus-card__badge">🎓 Студент</span>
          </div>

          <div className="bonus-card__amount">
            <div className="bonus-card__number">320</div>
            <div className="bonus-card__unit">баллов накоплено</div>
          </div>

          <div className="bonus-card__footer">
            <button
              className="bonus-card__cta"
              onClick={() => handleAction('/profile')}
            >
              Профиль →
            </button>
            <span className="bonus-card__id">#{user?.id ?? '000000'}</span>
          </div>
        </div>

        {/* Быстрые действия */}
        <div className="quick-actions">
          <button
            className="action-card action-card--primary"
            onClick={() => handleAction('/new-order')}
          >
            <span className="action-card__icon">📝</span>
            <div className="action-card__content">
              <span className="action-card__title">Новая заявка</span>
              <span className="action-card__sub">Оформить быстро</span>
            </div>
          </button>

          <button
            className="action-card action-card--green"
            onClick={() => handleAction('/orders')}
          >
            <span className="action-card__icon">📋</span>
            <div className="action-card__content">
              <span className="action-card__title">Мои заявки</span>
              <span className="action-card__sub">История</span>
            </div>
          </button>

          <button
            className="action-card action-card--surface"
            onClick={() => handleAction('/faq')}
          >
            <span className="action-card__icon">💬</span>
            <div className="action-card__content">
              <span className="action-card__title">FAQ</span>
              <span className="action-card__sub">Ответы</span>
            </div>
          </button>

          <button
            className="action-card action-card--light"
            onClick={() => window.open('https://t.me/ngueu_helper_bot', '_blank')}
          >
            <span className="action-card__icon">🎧</span>
            <div className="action-card__content">
              <span className="action-card__title">Поддержка</span>
              <span className="action-card__sub">Онлайн</span>
            </div>
          </button>
        </div>

        {/* Превью заявок */}
        {MOCK_ORDERS.length > 0 && (
          <div className="orders-preview">
            <div className="orders-preview__header">
              <span className="orders-preview__title">Последние заявки</span>
              <button
                className="orders-preview__link"
                onClick={() => handleAction('/orders')}
              >
                Все →
              </button>
            </div>

            {MOCK_ORDERS.map((order) => (
              <div
                key={order.id}
                className="order-row"
                onClick={() => handleAction(`/orders/${order.id}`)}
              >
                <div className="order-row__icon">{order.icon}</div>
                <div className="order-row__content">
                  <p className="order-row__name">{order.title}</p>
                  <p className="order-row__meta">{order.date}</p>
                </div>
                <div className="order-row__right">
                  <span className="order-row__price">{order.price}</span>
                  <StatusBadge status={order.status} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Инфо-секция */}
        <div className="info-section">
          <div className="section-header">
            <span className="section-title">О сервисе</span>
          </div>

          <div className="info-card" onClick={() => handleAction('/faq')}>
            <div className="info-card__icon">❓</div>
            <div className="info-card__content">
              <p className="info-card__title">FAQ и ответы</p>
              <p className="info-card__sub">Как работает сервис, гарантии, оплата</p>
            </div>
            <span className="info-card__arrow">›</span>
          </div>

          <div
            className="info-card"
            onClick={() => window.open('https://t.me/ngueu_helper_bot', '_blank')}
          >
            <div className="info-card__icon">📣</div>
            <div className="info-card__content">
              <p className="info-card__title">Новости и акции</p>
              <p className="info-card__sub">Следи за обновлениями в боте</p>
            </div>
            <span className="info-card__arrow">›</span>
          </div>
        </div>
      </div>
    </div>
  )
}
