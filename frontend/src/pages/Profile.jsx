import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL, getApiHeaders } from '../config'

export default function Profile() {
  const { user, haptic, tg, initData } = useTelegram()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [bonusHistory, setBonusHistory] = useState([])
  const [orderCount, setOrderCount] = useState(0)
  const [referralData, setReferralData] = useState(null)
  const [loading, setLoading] = useState(true)

  const userId = user?.id;
  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Студент'

  useEffect(() => {
    async function fetchData() {
      if (!userId) return;

      try {
        const headers = getApiHeaders(initData);

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

    if (userId) {
      fetchData();
    } else {
      setLoading(false);
    }
  }, [userId, initData]);

  function handleCopyLink() {
    if (!referralData?.link) return;
    haptic('notification', 'success');

    if (tg?.setClipboardText) {
      tg.setClipboardText(referralData.link);
    } else {
      navigator.clipboard.writeText(referralData.link);
    }
    tg?.showAlert?.('Ссылка скопирована! Отправь её друзьям.');
  }

  function handleShare() {
    if (!referralData?.link) return;
    haptic('impact', 'medium');
    const text = 'Привет! Пользуюсь крутым сервисом для учёбы в НГУЭУ. Залетай по моей ссылке и получи +500 бонусов на первый заказ! 🎓';

    const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(referralData.link)}&text=${encodeURIComponent(text)}`;
    if (tg?.openTelegramLink) {
      tg.openTelegramLink(shareUrl);
    } else {
      window.open(shareUrl, '_blank');
    }
  }

  const getLoyaltyLabel = (level) => {
    const levels = { novice: '🌱 Новичок', student: '🎓 Студент', regular: '⭐ Постоянный', vip: '👑 VIP' };
    return levels[level] || '🌱 Новичок';
  };

  const handleItem = (fn) => {
    haptic('impact', 'light');
    fn();
  };

  if (!userId && !loading) return <div className="profile-page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><p>Авторизация Telegram...</p></div>
  if (loading) return <div className="profile-page"><p style={{ textAlign: 'center', marginTop: 50 }}>Загрузка...</p></div>

  return (
    <div className="profile-page">
      <div className="profile-page__container">
        {/* Hero — аватар + имя */}
        <div className="profile-hero">
          <div className="profile-hero__avatar">
            {user?.photo_url
              ? <img src={user.photo_url} alt="" className="profile-hero__avatar-img" />
              : displayName[0]?.toUpperCase() ?? '👤'
            }
          </div>
          <div className="profile-hero__info">
            <div className="profile-hero__name">{displayName}</div>
            {user?.username && (
              <div className="profile-hero__id">@{user.username}</div>
            )}
          </div>
          <div className="profile-hero__uid">ID: {userId || '...'}</div>
        </div>

        {/* Лояльность + Статистика + История баллов — общий блок */}
        <div className="profile-overview">
          <div className="profile-loyalty">
            <div className="profile-loyalty__left">
              <p className="profile-loyalty__level">
                {profile ? getLoyaltyLabel(profile.loyalty_level) : '🌱 Новичок'}
              </p>
              <p className="profile-loyalty__hint">Уровень лояльности</p>
            </div>
            <div className="profile-loyalty__progress">
              <div className="profile-loyalty__bar">
                <div className="profile-loyalty__fill" style={{ width: `${Math.min((orderCount / 5) * 100, 100)}%` }} />
              </div>
              <p className="profile-loyalty__next">до след. уровня: {Math.max(5 - orderCount, 0)} заказов</p>
            </div>
          </div>

          <div className="profile-stats">
            <div className="profile-stat profile-stat--blue">
              <div className="profile-stat__value">{orderCount}</div>
              <div className="profile-stat__label">Заявки</div>
            </div>
            <div className="profile-stat profile-stat--green">
              <div className="profile-stat__value">{profile ? Math.floor(profile.bonus_balance) : '0'}</div>
              <div className="profile-stat__label">Баллы</div>
            </div>
            <div className="profile-stat profile-stat--yellow">
              <div className="profile-stat__value">5.0</div>
              <div className="profile-stat__label">Рейтинг</div>
            </div>
          </div>

          {/* История баллов */}
          <div className="profile-bonus-section">
            <div className="profile-bonus__header">
              <p className="profile-bonus__title">История баллов</p>
              <p className="profile-bonus__balance">{profile ? Math.floor(profile.bonus_balance) : '0'} баллов на счёте</p>
            </div>
            {bonusHistory.length === 0 ? (
              <div className="profile-bonus__empty">
                <p className="profile-bonus__empty-text">Транзакций пока нет</p>
              </div>
            ) : (
              <div className="profile-bonus__list">
                {bonusHistory.slice(0, 5).map((tx) => (
                  <div key={tx.id} className="profile-bonus__item">
                    <div className={`profile-bonus__item-dot ${tx.amount > 0 ? 'profile-bonus__item-dot--positive' : 'profile-bonus__item-dot--negative'}`} />
                    <div className="profile-bonus__item-info">
                      <p className="profile-bonus__item-desc">{tx.description}</p>
                      <p className="profile-bonus__item-date">{new Date(tx.created_at).toLocaleDateString()}</p>
                    </div>
                    <span className={`profile-bonus__item-amount ${tx.amount > 0 ? 'profile-bonus__item-amount--positive' : 'profile-bonus__item-amount--negative'}`}>
                      {tx.amount > 0 ? `+${Math.floor(tx.amount)}` : Math.floor(tx.amount)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Реферальная программа */}
        <div className="profile-referral">
          <p className="profile-referral__label">🎁 Реферальная программа</p>
          <h3 className="profile-referral__title">Пригласи друга — получи 100 ₽</h3>
          <p className="profile-referral__desc">
            Друг получит <b>500 баллов</b> при регистрации, а ты — <b>100 баллов</b> после его первой покупки
          </p>

          <div className="profile-referral__stats">
            <div className="profile-referral__stat-item">
              <span className="profile-referral__stat-value">{referralData?.stats?.total_invited || 0}</span>
              <span className="profile-referral__stat-label">Приглашено</span>
            </div>
            <div className="profile-referral__stat-item">
              <span className="profile-referral__stat-value">{referralData?.stats?.bonus_earned || 0} ₽</span>
              <span className="profile-referral__stat-label">Заработано</span>
            </div>
          </div>

          <div className="profile-referral__buttons">
            <button className="profile-referral__btn-share" onClick={handleShare}>
              Пригласить друга
            </button>
            <button className="profile-referral__btn-copy" onClick={handleCopyLink}>
              🔗
            </button>
          </div>
        </div>

        {/* Быстрые действия — сетка 2x2 как на главной */}
        <p className="profile-section-label">Быстрые действия</p>
        <div className="profile-actions">
          <button
            className="profile-action profile-action--blue"
            onClick={() => handleItem(() => navigate('/orders'))}
          >
            <span className="profile-action__icon">📋</span>
            <div className="profile-action__content">
              <span className="profile-action__title">Мои заявки</span>
              <span className="profile-action__sub">История</span>
            </div>
          </button>

          <button
            className="profile-action profile-action--green"
            onClick={() => handleItem(() => window.open('https://t.me/zachetlearning/13', '_blank'))}
          >
            <span className="profile-action__icon">🎧</span>
            <div className="profile-action__content">
              <span className="profile-action__title">Поддержка</span>
              <span className="profile-action__sub">Онлайн</span>
            </div>
          </button>

          <button
            className="profile-action profile-action--yellow"
            onClick={() => handleItem(() => window.open('https://docs.google.com/document/d/1G-BlXmQekS_RLzKfBvcfzyALkWECiisG2jHiH6j4jzs/mobilebasic', '_blank'))}
          >
            <span className="profile-action__icon">🏢</span>
            <div className="profile-action__content">
              <span className="profile-action__title">О сервисе</span>
              <span className="profile-action__sub">Документы</span>
            </div>
          </button>

          <button
            className="profile-action profile-action--light"
            onClick={() => {
              haptic('notification', 'warning')
              localStorage.removeItem('onboarding_done')
              navigate('/onboarding', { replace: true })
            }}
          >
            <span className="profile-action__icon">🔄</span>
            <div className="profile-action__content">
              <span className="profile-action__title">Онбординг</span>
              <span className="profile-action__sub">Заново</span>
            </div>
          </button>
        </div>

      </div>
    </div>
  )
}
