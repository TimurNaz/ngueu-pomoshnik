/**
 * OrderProgress — визуальный прогресс-бар по этапам заявки.
 * Поддерживает два режима: по номеру шага (step) или по статусу заказа (status).
 */
const STEPS = [
  { label: 'Заявка', icon: '📥' },
  { label: 'Цена', icon: '💰' },
  { label: 'Оплата', icon: '💳' },
  { label: 'В работе', icon: '⚙️' },
  { label: 'Проверка', icon: '📋' },
  { label: 'Готово', icon: '✅' },
]

const STATUS_TO_STEP = {
  new: 0,
  assigned: 0,
  priced: 1,
  paid: 2,
  in_progress: 3,
  review: 3,
  done: 4,
  confirming: 4,
  completed: 5,
  disputed: 4,
  canceled: 0,
}

export default function OrderProgress({ currentStep, status }) {
  const active = status ? (STATUS_TO_STEP[status] ?? 0) : (currentStep ?? 0)
  const lineWidth = active === 0 ? 0 : `${(active / (STEPS.length - 1)) * 100}%`

  return (
    <div className="order-progress">
      <p className="order-progress__title">Статус заявки</p>
      <div className="order-progress__steps">
        <div className="order-progress__line" style={{ width: lineWidth }} />

        {STEPS.map((s, i) => {
          const isDone = i < active
          const isActive = i === active

          return (
            <div
              key={s.label}
              className={`progress-step${isDone ? ' progress-step--done' : ''}${isActive ? ' progress-step--active' : ''}`}
            >
              <div className="progress-step__dot">
                {isDone ? '✓' : s.icon}
              </div>
              <span className="progress-step__label">{s.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
