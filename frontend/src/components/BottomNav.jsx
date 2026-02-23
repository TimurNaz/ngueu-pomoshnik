import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', icon: '🏠', label: 'Главная', exact: true },
  { to: '/orders', icon: '📋', label: 'Заявки' },
  { to: '/new-order', icon: '➕', label: 'Заказать' },
  { to: '/faq', icon: '💬', label: 'FAQ' },
  { to: '/profile', icon: '👤', label: 'Профиль' },
]

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      <div className="bottom-nav__inner">
        {NAV_ITEMS.map(({ to, icon, label, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              `bottom-nav__item${isActive ? ' active' : ''}`
            }
          >
            <span className="bottom-nav__icon">{icon}</span>
            <span className="bottom-nav__label">{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
