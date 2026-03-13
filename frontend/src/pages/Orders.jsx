import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL } from '../config'
import StatusBadge from '../components/ui/StatusBadge'
import OrderProgress from '../components/ui/OrderProgress'

const FILTERS = [
  { id: 'all', label: 'Все' },
  { id: 'new', label: 'Новые' },
  { id: 'assigned', label: 'Назначены' },
  { id: 'in_progress', label: 'В работе' },
  { id: 'done', label: 'Выполнены' },
  { id: 'canceled', label: 'Отменены' },
]

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState('all')
  const navigate = useNavigate()
  const { user } = useTelegram()
  
  const userId = user?.id || 927125510;

  useEffect(() => {
    async function fetchOrders() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/orders/client/${userId}`, {
          headers: {
            'bypass-tunnel-reminder': 'true'
          }
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
    fetchOrders();
  }, [userId]);

  const filtered =
    activeFilter === 'all'
      ? orders
      : orders.filter((o) => o.status === activeFilter)

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

              {order.status === 'in_progress' && (
                <div className="order-card__progress">
                  <OrderProgress currentStep={order.step} />
                </div>
              )}

              <div className="order-card__footer">
                <span className="order-card__price">
                  {order.price ? `${order.price} ₽` : 'Цена уточняется'}
                </span>
                <span style={{ color: 'var(--text-muted)', fontSize: 20 }}>›</span>
              </div>
            </div>
          ))
        )}

        {filtered.length > 0 && (
          <button
            className="btn btn--green"
            style={{marginTop: 20}}
            onClick={() => navigate('/new-order')}
          >
            📝 Оформить новую заявку
          </button>
        )}
      </div>
    </div>
  )
}
