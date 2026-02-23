const STATUS_MAP = {
  new: { label: 'Новая', className: 'badge--new', icon: '🆕' },
  assigned: { label: 'Назначена', className: 'badge--progress', icon: '👤' },
  in_progress: { label: 'В работе', className: 'badge--progress', icon: '⚙️' },
  done: { label: 'Выполнена', className: 'badge--done', icon: '✅' },
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
