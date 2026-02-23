/**
 * Универсальная карточка: primary (акцентная кнопка) или outline (информационная).
 * @param {object} props
 * @param {'primary'|'outline'} [props.variant]
 * @param {string} [props.icon] — эмодзи или иконка
 * @param {string} [props.title]
 * @param {string} [props.text]
 * @param {string} [props.href] — если задан, рендерится как <a>
 * @param {function} [props.onClick]
 * @param {React.ReactNode} [props.children] — контент вместо title/text
 * @param {boolean} [props.small] — уменьшенный вариант (иконка и шрифты)
 */
export default function Card({
  variant = 'outline',
  icon,
  title,
  text,
  href,
  onClick,
  children,
  small = false,
}) {
  const isPrimary = variant === 'primary'
  const className = [
    'card',
    isPrimary ? 'card--primary' : 'card--outline',
    small && 'card--small',
  ]
    .filter(Boolean)
    .join(' ')

  const content = children ?? (
    <>
      {icon && (
        <span className={`card__icon ${small ? 'card__icon--small' : ''}`} aria-hidden>
          {icon}
        </span>
      )}
      <div className="card__content">
        {title && (
          <h2 className={`card__title ${small ? 'card__title--small' : ''}`}>{title}</h2>
        )}
        {text && (
          <p className={`card__text ${small ? 'card__text--muted' : ''}`}>{text}</p>
        )}
      </div>
      {isPrimary && !children && <span className="card__arrow" aria-hidden>→</span>}
    </>
  )

  if (href) {
    return (
      <a href={href} className={className}>
        {content}
      </a>
    )
  }

  const Tag = onClick ? 'button' : 'div'
  return (
    <Tag className={className} type={onClick ? 'button' : undefined} onClick={onClick}>
      {content}
    </Tag>
  )
}
