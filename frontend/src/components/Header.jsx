import { useTelegram } from '../hooks/useTelegram'

export default function Header() {
  const { haptic } = useTelegram()

  return (
    <header className="header">
      <div className="header__inner">
        <div className="header__logo">
          <div className="header__logo-icon">🎓</div>
          <div className="header__logo-text">
            <span className="header__title">НГУЭУ/Помощник</span>
            <span className="header__subtitle">Учебные работы</span>
          </div>
        </div>
        <button
          className="header__action"
          onClick={() => haptic('notification', 'success')}
          aria-label="Уведомления"
        >
          🔔
        </button>
      </div>
    </header>
  )
}
