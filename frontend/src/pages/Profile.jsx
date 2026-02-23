import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'

export default function Profile() {
  const { user, haptic } = useTelegram()
  const navigate = useNavigate()

  const displayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Студент'

  function handleItem(action) {
    haptic('impact', 'light')
    action()
  }

  return (
    <div className="profile-page">
      <div className="profile-page__container">
        {/* Hero */}
        <div className="profile-hero">
          <div className="profile-hero__avatar">
            {displayName[0]?.toUpperCase() ?? '👤'}
          </div>
          <div className="profile-hero__name">{displayName}</div>
          {user?.username && (
            <div className="profile-hero__id">@{user.username}</div>
          )}

          {/* Статистика */}
          <div className="profile-stats">
            <div className="profile-stat">
              <div className="profile-stat__value">3</div>
              <div className="profile-stat__label">Заявки</div>
            </div>
            <div className="profile-stat">
              <div className="profile-stat__value">320</div>
              <div className="profile-stat__label">Баллы</div>
            </div>
            <div className="profile-stat">
              <div className="profile-stat__value">4.8</div>
              <div className="profile-stat__label">Рейтинг</div>
            </div>
          </div>
        </div>

        {/* Меню */}
        <div className="profile-menu">
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
            onClick={() => handleItem(() => navigate('/new-order'))}
          >
            <div className="profile-menu__icon profile-menu__icon--green">
              📝
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">Новая заявка</p>
              <p className="profile-menu__sub">Оформить работу</p>
            </div>
            <div className="profile-menu__right">›</div>
          </div>

          <div
            className="profile-menu__item"
            onClick={() =>
              handleItem(() =>
                window.open('https://t.me/ngueu_helper_bot', '_blank')
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

          <div
            className="profile-menu__item"
            onClick={() => handleItem(() => navigate('/faq'))}
          >
            <div className="profile-menu__icon profile-menu__icon--neutral">
              💬
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">FAQ</p>
              <p className="profile-menu__sub">Ответы на вопросы</p>
            </div>
            <div className="profile-menu__right">›</div>
          </div>
        </div>

        {/* О сервисе */}
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

          <div className="profile-menu__item">
            <div className="profile-menu__icon profile-menu__icon--neutral">
              📄
            </div>
            <div className="profile-menu__info">
              <p className="profile-menu__label">Пользовательское соглашение</p>
              <p className="profile-menu__sub">Правила использования</p>
            </div>
            <div className="profile-menu__right">›</div>
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
      </div>
    </div>
  )
}
