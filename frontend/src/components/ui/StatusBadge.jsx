const STATUS_MAP = {
  new: { label: 'Новая', className: 'badge--new', icon: '🆕' },
  assigned: { label: 'Назначена', className: 'badge--progress', icon: '👤' },
  priced: { label: 'К оплате', className: 'badge--priced', icon: '💰' },
  paid: { label: 'Оплачен', className: 'badge--paid', icon: '💳' },
  in_progress: { label: 'В работе', className: 'badge--progress', icon: '⚙️' },
  review: { label: 'На проверке', className: 'badge--review', icon: '👀' },
  done: { label: 'Выполнена', className: 'badge--done', icon: '✅' },
  confirming: { label: 'Проверка', className: 'badge--confirming', icon: '📋' },
  completed: { label: 'Завершён', className: 'badge--completed', icon: '🎉' },
  disputed: { label: 'Спор', className: 'badge--disputed', icon: '⚠️' },
  canceled: { label: 'Отменена', className: 'badge--canceled', icon: '❌' },
}

export default function StatusBadge({ status = 'new' }) {
  const { label, className, icon } = STATUS_MAP[status] ?? STATUS_MAP.new
  return (
    <span className={`badge ${className}`}>
      {icon} {label}
    </span>
  )
}
