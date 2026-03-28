import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', icon: '/images/nav/home.svg', label: 'Главная', exact: true },
  { to: '/orders', icon: '/images/nav/document.svg', label: 'Заявки' },
  { to: '/new-order', icon: '/images/nav/add.svg', label: 'Заказать' },
  { to: '/faq', icon: '/images/nav/comment-info.svg', label: 'FAQ' },
  { to: '/profile', icon: '/images/nav/user.svg', label: 'Профиль' },
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
            <div className="bottom-nav__icon-wrap">
              <img src={icon} alt={label} className="bottom-nav__icon" />
            </div>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
