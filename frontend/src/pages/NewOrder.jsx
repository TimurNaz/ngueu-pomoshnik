import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import { API_BASE_URL } from '../config'

const WORK_TYPES = [
  { id: 'coursework', label: '📊 Курсовая', emoji: '📊' },
  { id: 'diploma', label: '🎓 Диплом', emoji: '🎓' },
  { id: 'abstract', label: '📄 Реферат', emoji: '📄' },
  { id: 'lab', label: '🔬 Лабораторная', emoji: '🔬' },
  { id: 'practice', label: '🏢 Практика', emoji: '🏢' },
  { id: 'other', label: '📌 Другое', emoji: '📌' },
]

const URGENCY = [
  { id: '3d', label: 'До 3 дней' },
  { id: '1w', label: '1 неделя' },
  { id: '2w', label: '2 недели' },
  { id: '1m', label: 'Больше месяца' },
]

const INITIAL_STATE = {
  workType: '',
  subject: '',
  topic: '',
  teacher: '',
  requirements: '',
  deadline: '',
  urgency: '',
  antiplagiat: '',
  contactInfo: '',
}

export default function NewOrder() {
  const [form, setForm] = useState(INITIAL_STATE)
  const [errors, setErrors] = useState({})
  const [step, setStep] = useState(1) // 1 = тип/тема, 2 = детали, 3 = итог
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const { haptic, user } = useTelegram()

  function set(key, value) {
    setForm((f) => ({ ...f, [key]: value }))
    if (errors[key]) setErrors((e) => ({ ...e, [key]: '' }))
  }

  function validate1() {
    const e = {}
    if (!form.workType) e.workType = 'Выберите тип работы'
    if (!form.subject.trim()) e.subject = 'Укажите дисциплину'
    if (!form.topic.trim()) e.topic = 'Укажите тему'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  function validate2() {
    const e = {}
    if (!form.urgency) e.urgency = 'Укажите срочность'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  function nextStep() {
    haptic('impact', 'light')
    if (step === 1 && !validate1()) return
    if (step === 2 && !validate2()) return
    setStep((s) => s + 1)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function submit() {
    haptic('notification', 'success')
    setSubmitting(true)
    
    // Берем ID пользователя из Telegram
    const userId = user?.id || 927125510; // Фолбэк для тестов

    const orderData = {
      client_id: userId,
      work_type: form.workType,
      subject: form.subject,
      topic: form.topic,
      teacher: form.teacher || null,
      requirements: form.requirements || null,
      antiplagiat_percent: (form.antiplagiat && form.antiplagiat !== 'discuss') ? parseInt(form.antiplagiat) : null,
      deadline: form.deadline ? new Date(form.deadline).toISOString() : null,
      urgency: form.urgency
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'bypass-tunnel-reminder': 'true',
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Ошибка: ${errorText}`);
      }

      setSubmitting(false)
      navigate('/orders', { state: { newOrder: true } })
    } catch (error) {
      console.error('Submission error:', error);
      alert('⚠️ Не удалось отправить заявку. Пожалуйста, попробуйте позже.');
      setSubmitting(false)
    }
  }

  const selectedType = WORK_TYPES.find((t) => t.id === form.workType)

  return (
    <div className="order-form-page">
      <div className="order-form-page__container">
        {/* Hero */}
        <div className="order-form-hero">
          <span className="order-form-hero__icon">
            {selectedType?.emoji ?? '📝'}
          </span>
          <div>
            <h1 className="order-form-hero__title">Новая заявка</h1>
            <p className="order-form-hero__sub">
              {step === 1 && 'Шаг 1 из 3 — Тип и тема работы'}
              {step === 2 && 'Шаг 2 из 3 — Детали и требования'}
              {step === 3 && 'Шаг 3 из 3 — Проверьте и отправьте'}
            </p>
          </div>
        </div>

        {/* ШАГ 1 — Тип и тема */}
        {step === 1 && (
          <>
            <div className="form-card">
              <h2 className="form-card__title">Тип работы</h2>
              <div className="work-types">
                {WORK_TYPES.map((type) => (
                  <button
                    key={type.id}
                    className={`work-type-chip${form.workType === type.id ? ' selected' : ''}`}
                    onClick={() => set('workType', type.id)}
                  >
                    {type.label}
                  </button>
                ))}
              </div>
              {errors.workType && (
                <p className="form-error">{errors.workType}</p>
              )}
            </div>

            <div className="form-card">
              <h2 className="form-card__title">Тема и дисциплина</h2>

              <div className="form-group">
                <label className="form-label">
                  Дисциплина <span>*</span>
                </label>
                <input
                  className={`form-input${errors.subject ? ' form-input--error' : ''}`}
                  placeholder="Например: Экономическая теория"
                  value={form.subject}
                  onChange={(e) => set('subject', e.target.value)}
                />
                {errors.subject && (
                  <p className="form-error">{errors.subject}</p>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">
                  Тема работы <span>*</span>
                </label>
                <input
                  className={`form-input${errors.topic ? ' form-input--error' : ''}`}
                  placeholder="Введите тему или напишите 'по согласованию'"
                  value={form.topic}
                  onChange={(e) => set('topic', e.target.value)}
                />
                {errors.topic && <p className="form-error">{errors.topic}</p>}
              </div>

              <div className="form-group">
                <label className="form-label">Преподаватель</label>
                <input
                  className="form-input"
                  placeholder="ФИО преподавателя (если известно)"
                  value={form.teacher}
                  onChange={(e) => set('teacher', e.target.value)}
                />
                <p className="form-hint">
                  Поможет подобрать исполнителя, знакомого с требованиями
                </p>
              </div>
            </div>

            <button className="btn btn--primary" onClick={nextStep}>
              Далее →
            </button>
          </>
        )}

        {/* ШАГ 2 — Детали */}
        {step === 2 && (
          <>
            <div className="form-card">
              <h2 className="form-card__title">Срочность</h2>
              <div className="urgency-chips">
                {URGENCY.map((u) => (
                  <button
                    key={u.id}
                    className={`urgency-chip${form.urgency === u.id ? ' selected' : ''}`}
                    onClick={() => set('urgency', u.id)}
                  >
                    {u.label}
                  </button>
                ))}
              </div>
              {errors.urgency && (
                <p className="form-error" style={{ marginTop: 8 }}>
                  {errors.urgency}
                </p>
              )}
            </div>

            <div className="form-card">
              <h2 className="form-card__title">Требования к работе</h2>

              <div className="form-group">
                <label className="form-label">Требования и методичка</label>
                <textarea
                  className="form-textarea"
                  placeholder="Опишите требования: объём, оформление, источники, особые пожелания..."
                  value={form.requirements}
                  onChange={(e) => set('requirements', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Антиплагиат</label>
                <select
                  className="form-select"
                  value={form.antiplagiat}
                  onChange={(e) => set('antiplagiat', e.target.value)}
                >
                  <option value="">Не требуется</option>
                  <option value="70">Не менее 70%</option>
                  <option value="75">Не менее 75%</option>
                  <option value="80">Не менее 80%</option>
                  <option value="85">Не менее 85%</option>
                  <option value="discuss">Уточнить у исполнителя</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Дедлайн (дата сдачи)</label>
                <input
                  type="date"
                  className="form-input"
                  value={form.deadline}
                  onChange={(e) => set('deadline', e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
            </div>

            <div className="form-notice">
              <span className="form-notice__icon">💡</span>
              <p className="form-notice__text">
                Чем подробнее вы опишете требования, тем точнее будет подобран
                исполнитель и цена работы.
              </p>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button
                className="btn btn--ghost btn--auto"
                style={{ flex: 1 }}
                onClick={() => setStep(1)}
              >
                ← Назад
              </button>
              <button
                className="btn btn--primary"
                style={{ flex: 2 }}
                onClick={nextStep}
              >
                Далее →
              </button>
            </div>
          </>
        )}

        {/* ШАГ 3 — Итог */}
        {step === 3 && (
          <>
            <div className="order-summary">
              <h2 className="order-summary__title">📋 Итого по заявке</h2>

              <div className="summary-row">
                <span className="summary-row__label">Тип работы</span>
                <span className="summary-row__value">
                  {selectedType?.label ?? '—'}
                </span>
              </div>
              <div className="summary-divider" />

              <div className="summary-row">
                <span className="summary-row__label">Дисциплина</span>
                <span className="summary-row__value">{form.subject || '—'}</span>
              </div>
              <div className="summary-divider" />

              <div className="summary-row">
                <span className="summary-row__label">Тема</span>
                <span className="summary-row__value">{form.topic || '—'}</span>
              </div>
              <div className="summary-divider" />

              {form.teacher && (
                <>
                  <div className="summary-row">
                    <span className="summary-row__label">Преподаватель</span>
                    <span className="summary-row__value">{form.teacher}</span>
                  </div>
                  <div className="summary-divider" />
                </>
              )}

              <div className="summary-row">
                <span className="summary-row__label">Срочность</span>
                <span className="summary-row__value">
                  {URGENCY.find((u) => u.id === form.urgency)?.label ?? '—'}
                </span>
              </div>
              <div className="summary-divider" />

              {form.antiplagiat && (
                <>
                  <div className="summary-row">
                    <span className="summary-row__label">Антиплагиат</span>
                    <span className="summary-row__value">
                      {form.antiplagiat === 'discuss' ? 'Уточнить' : `≥ ${form.antiplagiat}%`}
                    </span>
                  </div>
                  <div className="summary-divider" />
                </>
              )}

              <div className="summary-row summary-row--total">
                <span className="summary-row__label">Цена</span>
                <span className="summary-row__value">По договорённости</span>
              </div>
            </div>

            <div className="form-notice">
              <span className="form-notice__icon">⚡</span>
              <p className="form-notice__text">
                После отправки администратор подберёт исполнителя и свяжется с
                вами в течение нескольких часов с ценой.
              </p>
            </div>

            <div style={{ display: 'flex', gap: 10 }}>
              <button
                className="btn btn--ghost btn--auto"
                style={{ flex: 1 }}
                onClick={() => setStep(2)}
              >
                ← Назад
              </button>
              <button
                className="btn btn--green"
                style={{ flex: 2 }}
                onClick={submit}
                disabled={submitting}
              >
                {submitting ? '⏳ Отправка...' : '🚀 Отправить заявку'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
