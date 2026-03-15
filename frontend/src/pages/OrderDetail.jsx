import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import StatusBadge from '../components/ui/StatusBadge'
import OrderProgress from '../components/ui/OrderProgress'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL, getApiHeaders } from '../config'

export default function OrderDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { haptic, initData } = useTelegram()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    async function fetchOrder() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/orders/${id}`, {
          headers: getApiHeaders(initData)
        });
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        setOrder(data);
      } catch (err) {
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchOrder();
  }, [id, initData]);

  async function handleCancel() {
    if (!window.confirm('Вы уверены, что хотите отменить эту заявку?')) return;
    
    haptic('notification', 'warning')
    setCancelling(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/orders/${id}/cancel`, {
        method: 'POST',
        headers: getApiHeaders(initData)
      });
      if (response.ok) {
        alert('Заявка успешно отменена');
        navigate('/orders');
      } else {
        throw new Error('Failed to cancel');
      }
    } catch (err) {
      alert('Ошибка при отмене заявки');
    } finally {
      setCancelling(false)
    }
  }

  if (loading) return <div className="order-detail"><p style={{textAlign: 'center', marginTop: 50}}>Загрузка...</p></div>
  if (!order) return <div className="order-detail"><p style={{textAlign: 'center', marginTop: 50}}>Заявка не найдена</p></div>

  const getWorkIcon = (type) => {
    const icons = { coursework: '📊', diploma: '🎓', abstract: '📄', lab: '🔬', practice: '🏢' };
    return icons[type] || '📌';
  };

  const getWorkLabel = (type) => {
    const labels = { coursework: 'Курсовая', diploma: 'Диплом', abstract: 'Реферат', lab: 'Лабораторная', practice: 'Практика' };
    return labels[type] || 'Другое';
  };

  const getFullFileUrl = (path) => {
    if (path.startsWith('http')) return path;
    return `${API_BASE_URL}${path}`;
  };

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
        <OrderProgress currentStep={order.step} />

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

        {/* ПРИКРЕПЛЕННЫЕ ФАЙЛЫ */}
        {order.attachments && order.attachments.length > 0 && (
          <div className="form-card" style={{ gap: 10, marginTop: 20 }}>
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
          <div className="form-card" style={{ gap: 8, marginTop: 20 }}>
            <h3 className="form-card__title">Требования</h3>
            <p style={{ fontSize: 'var(--font-size-md)', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {order.requirements}
            </p>
          </div>
        )}

        <div style={{marginTop: 30, display: 'flex', flexDirection: 'column', gap: 12}}>
            {order.status === 'new' && (
                <button 
                    className="btn btn--danger" 
                    onClick={handleCancel}
                    disabled={cancelling}
                    style={{backgroundColor: '#ff4d4f', color: 'white'}}
                >
                    {cancelling ? '⏳ Отмена...' : '❌ Отменить заявку'}
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
