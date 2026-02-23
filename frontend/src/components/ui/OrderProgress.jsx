/**
 * OrderProgress — визуальный прогресс-бар по 4 этапам заявки.
 * @param {number} currentStep — 0..3 (0 = новая, 1 = исполнитель назначен, 2 = в работе, 3 = выполнена)
 */
const STEPS = [
  { label: 'Заявка принята', icon: '📥' },
  { label: 'Исполнитель назначен', icon: '👤' },
  { label: 'В работе', icon: '⚙️' },
  { label: 'Выполнено', icon: '✅' },
]

export default function OrderProgress({ currentStep = 0 }) {
  // Ширина заполненной линии в процентах
  const lineWidth = currentStep === 0 ? 0 : `${(currentStep / (STEPS.length - 1)) * 100}%`

  return (
    <div className="order-progress">
      <p className="order-progress__title">Статус заявки</p>
      <div className="order-progress__steps">
        {/* Заполненная линия */}
        <div className="order-progress__line" style={{ width: lineWidth }} />

        {STEPS.map((step, i) => {
          const isDone = i < currentStep
          const isActive = i === currentStep

          return (
            <div
              key={step.label}
              className={`progress-step${isDone ? ' progress-step--done' : ''}${isActive ? ' progress-step--active' : ''}`}
            >
              <div className="progress-step__dot">
                {isDone ? '✓' : step.icon}
              </div>
              <span className="progress-step__label">{step.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
