import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import StatusBadge from '../components/ui/StatusBadge'
import { API_BASE_URL, getApiHeaders } from '../config'

export default function Home() {
  const navigate = useNavigate()
  const { user, haptic, initData } = useTelegram()
  const [profile, setProfile] = useState(null)
  const [latestOrders, setLatestOrders] = useState([])
  const [loading, setLoading] = useState(true)

  // Используем ID только из Telegram
  const userId = user?.id;
  const displayName = user?.first_name ?? 'Студент'

  useEffect(() => {
    async function fetchData() {
      if (!userId) return;

      try {
        const headers = getApiHeaders(initData);
        
        // Загружаем профиль
        const profRes = await fetch(`${API_BASE_URL}/api/users/${userId}`, { headers });
        if (profRes.ok) {
          const profData = await profRes.json();
          setProfile(profData);
        }

        // Загружаем последние заявки
        const ordersRes = await fetch(`${API_BASE_URL}/api/orders/latest/${userId}`, { headers });
        if (ordersRes.ok) {
          const ordersData = await ordersRes.json();
          setLatestOrders(ordersData);
        }
      } catch (err) {
        console.error('Home data fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    
    if (userId) {
        fetchData();
    } else {
        // Если мы не в Telegram, загрузка не закончится, пока не появится ID
        setLoading(false);
    }
  }, [userId, initData]);

  function handleAction(path) {
    haptic('impact', 'light')
    navigate(path)
  }

  const getWorkIcon = (type) => {
    const icons = { coursework: '📊', diploma: '🎓', abstract: '📄', lab: '🔬', practice: '🏢' };
    return icons[type] || '📌';
  };

  const getLoyaltyBadge = (level) => {
    const levels = { novice: '🌱 Новичок', student: '🎓 Студент', regular: '⭐ Постоянный', vip: '👑 VIP' };
    return levels[level] || '🌱 Новичок';
  };

  if (!userId && !loading) {
      return (
        <div className="home" style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}>
            <p>Авторизация Telegram...</p>
        </div>
      )
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
            <span className="bonus-card__badge">
              {profile ? getLoyaltyBadge(profile.loyalty_level) : 'Загрузка...'}
            </span>
          </div>

          <div className="bonus-card__amount">
            <div className="bonus-card__number">
              {profile ? Math.floor(profile.bonus_balance) : '0'}
            </div>
            <div className="bonus-card__unit">баллов накоплено</div>
          </div>

          <div className="bonus-card__footer">
            <button
              className="bonus-card__cta"
              onClick={() => handleAction('/profile')}
            >
              Профиль →
            </button>
            <span className="bonus-card__id">#{userId || '...'}</span>
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
            onClick={() => window.open('https://t.me/ngueu_bot_support', '_blank')}
          >
            <span className="action-card__icon">🎧</span>
            <div className="action-card__content">
              <span className="action-card__title">Поддержка</span>
              <span className="action-card__sub">Онлайн</span>
            </div>
          </button>
        </div>

        {/* Превью заявок */}
        {!loading && latestOrders.length > 0 && (
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

            {latestOrders.map((order) => (
              <div
                key={order.id}
                className="order-row"
                onClick={() => handleAction(`/orders/${order.id}`)}
              >
                <div className="order-row__icon">{getWorkIcon(order.work_type)}</div>
                <div className="order-row__content">
                  <p className="order-row__name">{order.subject}</p>
                  <p className="order-row__meta">{new Date(order.created_at).toLocaleDateString()}</p>
                </div>
                <div className="order-row__right">
                  <span className="order-row__price">
                    {order.price ? `${Math.floor(order.price)} ₽` : 'Цена...'}
                  </span>
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
