import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL } from '../config'

export default function Profile() {
  const { user, haptic, tg } = useTelegram()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [bonusHistory, setBonusHistory] = useState([])
  const [orderCount, setOrderCount] = useState(0)
  const [referralData, setReferralData] = useState(null)
  const [loading, setLoading] = useState(true)

  const userId = user?.id || 927125510;
  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Студент'

  useEffect(() => {
    async function fetchData() {
      try {
        const headers = { 'bypass-tunnel-reminder': 'true' };
        
        const [profRes, bonusRes, ordersRes, refRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/users/${userId}`, { headers }),
          fetch(`${API_BASE_URL}/api/users/${userId}/bonuses`, { headers }),
          fetch(`${API_BASE_URL}/api/orders/client/${userId}`, { headers }),
          fetch(`${API_BASE_URL}/api/users/${userId}/referral`, { headers })
        ]);

        if (profRes.ok) setProfile(await profRes.json());
        if (bonusRes.ok) setBonusHistory(await bonusRes.json());
        if (ordersRes.ok) {
          const orders = await ordersRes.json();
          setOrderCount(orders.length);
        }
        if (refRes.ok) setReferralData(await refRes.json());

      } catch (err) {
        console.error('Profile fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [userId]);

  function handleCopyLink() {
    if (!referralData?.link) return;
    haptic('notification', 'success');
    
    // Пытаемся использовать стандартный метод Telegram если доступен
    if (tg?.setClipboardText) {
        tg.setClipboardText(referralData.link);
    } else {
        navigator.clipboard.writeText(referralData.link);
    }
    tg.showAlert('Ссылка скопирована! Отправь её друзьям.');
  }

  function handleShare() {
    if (!referralData?.link) return;
    haptic('impact', 'medium');
    const text = 'Привет! Пользуюсь крутым сервисом для учёбы в НГУЭУ. Залетай по моей ссылке и получи +500 бонусов на первый заказ! 🎓';
    const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(referralData.link)}&text=${encodeURIComponent(text)}`;
    tg.openTelegramLink(shareUrl);
  }

  const getLoyaltyLabel = (level) => {
    const levels = { novice: '🌱 Новичок', student: '🎓 Студент', regular: '⭐ Постоянный', vip: '👑 VIP' };
    return levels[level] || '🌱 Новичок';
  };

  if (loading) return <div className="profile-page"><p style={{textAlign: 'center', marginTop: 50}}>Загрузка...</p></div>

  return (
    <div className="profile-page">
      <div className="profile-page__container">
        {/* Hero */}
        <div className="profile-hero">
          <div className="profile-hero__avatar">
            {displayName[0]?.toUpperCase() ?? '👤'}
          </div>
          <div className="profile-hero__name">{displayName}</div>
          <div className="profile-hero__badge">
            {profile ? getLoyaltyLabel(profile.loyalty_level) : '🌱 Новичок'}
          </div>
          {user?.username && (
            <div className="profile-hero__id">@{user.username}</div>
          )}

          {/* Статистика */}
          <div className="profile-stats">
            <div className="profile-stat">
              <div className="profile-stat__value">{orderCount}</div>
              <div className="profile-stat__label">Заявки</div>
            </div>
            <div className="profile-stat">
              <div className="profile-stat__value">{profile ? Math.floor(profile.bonus_balance) : '0'}</div>
              <div className="profile-stat__label">Баллы</div>
            </div>
            <div className="profile-stat">
              <div className="profile-stat__value">5.0</div>
              <div className="profile-stat__label">Рейтинг</div>
            </div>
          </div>
        </div>

        {/* РЕФЕРАЛЬНАЯ ПРОГРАММА */}
        <div className="form-card" style={{marginTop: 20, gap: 12, background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', border: '1px solid #bae6fd'}}>
          <h3 className="form-card__title" style={{fontSize: 16, color: '#0369a1'}}>🎁 Пригласи друга — получи 100 ₽</h3>
          <p style={{fontSize: 13, color: '#0c4a6e', lineHeight: 1.4}}>
            Твой друг получит <b>500 баллов</b> при регистрации, а ты — <b>100 баллов</b> после его первой покупки!
          </p>
          
          <div style={{display: 'flex', gap: 8, marginTop: 8}}>
            <button className="btn btn--primary" onClick={handleShare} style={{flex: 2, padding: '10px 0'}}>
              🚀 Пригласить
            </button>
            <button className="btn btn--ghost" onClick={handleCopyLink} style={{flex: 1, padding: '10px 0', border: '1px solid #0369a1', color: '#0369a1'}}>
              🔗 Ссылка
            </button>
          </div>

          {/* ТЕПЕРЬ ПОКАЗЫВАЕМ ВСЕГДА */}
          <div style={{marginTop: 10, paddingTop: 10, borderTop: '1px solid #bae6fd', display: 'flex', justifyContent: 'space-between'}}>
            <span style={{fontSize: 12, color: '#0369a1'}}>Приглашено: <b>{referralData?.stats?.total_invited || 0}</b></span>
            <span style={{fontSize: 12, color: '#0369a1'}}>Заработано: <b>{referralData?.stats?.bonus_earned || 0} ₽</b></span>
          </div>
        </div>

        {/* Блок бонусов */}
        <div className="form-card" style={{marginTop: 20, gap: 12}}>
          <h3 className="form-card__title" style={{fontSize: 16}}>История баллов</h3>
          {bonusHistory.length === 0 ? (
            <p style={{color: 'var(--text-muted)', fontSize: 14}}>Транзакций пока нет</p>
          ) : (
            <div style={{display: 'flex', flexDirection: 'column', gap: 10}}>
              {bonusHistory.slice(0, 5).map((tx) => (
                <div key={tx.id} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                  <div>
                    <p style={{fontSize: 14, fontWeight: 500}}>{tx.description}</p>
                    <p style={{fontSize: 12, color: 'var(--text-muted)'}}>{new Date(tx.created_at).toLocaleDateString()}</p>
                  </div>
                  <span style={{
                    fontWeight: 700, 
                    color: tx.amount > 0 ? 'var(--green)' : 'var(--accent)'
                  }}>
                    {tx.amount > 0 ? `+${Math.floor(tx.amount)}` : Math.floor(tx.amount)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Меню */}
        <div className="profile-menu" style={{marginTop: 20}}>
          <div
            className="profile-menu__item"
            onClick={() => handleItem(() => navigate('/orders'))}
          >
            <div className="profile-menu__icon profile-menu__icon--accent">
              📋
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">Мои заявки</p>
              <p className="profile-menu__sub">История и статусы</p>
            </div>
            <div className="profile-menu__right">›</div>
          </div>

          <div
            className="profile-menu__item"
            onClick={() =>
              handleItem(() =>
                window.open('https://t.me/ngueu_bot_support', '_blank')
              )
            }
          >
            <div className="profile-menu__icon profile-menu__icon--accent">
              🎧
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">Поддержка</p>
              <p className="profile-menu__sub">Написать администратору</p>
            </div>
            <div className="profile-menu__right">›</div>
          </div>
        </div>

        <div className="profile-menu">
          <div className="profile-menu__item">
            <div className="profile-menu__icon profile-menu__icon--neutral">
              🏢
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">О сервисе</p>
              <p className="profile-menu__sub">НГУЭУ/Помощник v1.0</p>
            </div>
          </div>

          <div
            className="profile-menu__item profile-menu__item--danger"
            onClick={() => {
              haptic('notification', 'warning')
              localStorage.removeItem('onboarding_done')
              navigate('/onboarding', { replace: true })
            }}
          >
            <div className="profile-menu__icon profile-menu__icon--neutral">
              🔄
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">Сбросить онбординг</p>
              <p className="profile-menu__sub">Просмотреть заново</p>
            </div>
          </div>
        </div>
        
        <p style={{textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', margin: '20px 0'}}>
          ID: {userId}
        </p>
      </div>
    </div>
  )
}
