import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL, getApiHeaders } from '../config'
import StatusBadge from '../components/ui/StatusBadge'
import OrderProgress from '../components/ui/OrderProgress'

const FILTERS = [
  { id: 'all', label: 'Все' },
  { id: 'active', label: 'Активные' },
  { id: 'priced', label: 'К оплате' },
  { id: 'paid', label: 'Оплачены' },
  { id: 'in_progress', label: 'В работе' },
  { id: 'confirming', label: 'Проверка' },
  { id: 'completed', label: 'Завершены' },
  { id: 'canceled', label: 'Отменены' },
]

const ACTIVE_STATUSES = ['new', 'assigned', 'priced', 'paid', 'in_progress', 'review', 'done', 'confirming', 'disputed']

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('all')
  const navigate = useNavigate()
  const { user, initData } = useTelegram()
  
  const userId = user?.id;

  useEffect(() => {
    async function fetchOrders() {
      if (!userId) return;

      try {
        const response = await fetch(`${API_BASE_URL}/api/orders/client/${userId}`, {
          headers: getApiHeaders(initData)
        });
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setOrders(data);
      } catch (err) {
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    
    if (userId) {
        fetchOrders();
    } else {
        setLoading(false);
    }
  }, [userId, initData]);

  const filtered =
    activeFilter === 'all'
      ? orders
      : activeFilter === 'active'
        ? orders.filter((o) => ACTIVE_STATUSES.includes(o.status))
        : orders.filter((o) => o.status === activeFilter)

  if (!userId && !loading) return <div className="orders-page" style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}><p>Авторизация Telegram...</p></div>
  if (loading) {
    return <div className="orders-page"><p style={{textAlign: 'center', marginTop: 50}}>Загрузка...</p></div>
  }

  const getWorkIcon = (type) => {
    const icons = { coursework: '📊', diploma: '🎓', abstract: '📄', lab: '🔬', practice: '🏢' };
    return icons[type] || '📌';
  };

  return (
    <div className="orders-page">
      <div className="orders-page__container">
        {/* Заголовок */}
        <div>
          <h1 className="orders-page__title">Мои заявки</h1>
          {orders.length > 0 && (
            <p className="orders-page__count">
              {orders.length} {orders.length === 1 ? 'заявка' : orders.length < 5 ? 'заявки' : 'заявок'}
            </p>
          )}
        </div>

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
              className="btn btn--green orders-page__cta"
              style={{ marginTop: 8 }}
              onClick={() => navigate('/new-order')}
            >
              Оформить заявку
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
                {getWorkIcon(order.work_type)} {order.subject}
              </h3>

              <div className="order-card__meta">
                <span className="order-card__meta-item">📅 {new Date(order.created_at).toLocaleDateString()}</span>
                {order.deadline && (
                  <span className="order-card__meta-item">
                    ⏰ Дедлайн: {new Date(order.deadline).toLocaleDateString()}
                  </span>
                )}
              </div>

              {!['new', 'canceled', 'completed'].includes(order.status) && (
                <div className="order-card__progress">
                  <OrderProgress status={order.status} />
                </div>
              )}

              <div className="order-card__footer">
                <span className="order-card__price">
                  {order.price ? `${order.price} ₽` : 'Цена уточняется'}
                </span>
                <img src="/images/chevron-right.svg" alt="" style={{ width: 24, height: 24 }} />
              </div>
            </div>
          ))
        )}

        {filtered.length > 0 && (
          <button
            className="btn btn--green orders-page__cta"
            style={{marginTop: 20}}
            onClick={() => navigate('/new-order')}
          >
            Оформить новую заявку
          </button>
        )}
      </div>
    </div>
  )
}
