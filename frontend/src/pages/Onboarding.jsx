import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'
import '../styles/components/onboarding.css'

const SLIDES = [
  {
    image: '/images/onboarding/slide1.svg',
    title: 'Добро пожаловать в StudHome!',
    description: 'Твое новое место для помощи в учебе. Здесь ты найдешь поддержку, проверенных исполнителей и атмосферу взаимовыручки.',
    bg: '#e23a49',
    ellipse: 'ellipse--slide1',
    theme: 'dark',
  },
  {
    image: '/images/onboarding/slide2.svg',
    title: 'Находите своих исполнителей',
    description: 'Выбирай специалистов под свои задачи — без лишних сложностей. У нас удобно, прозрачно и безопасно.',
    bg: '#fafafa',
    ellipse: 'ellipse--slide2',
    theme: 'light',
  },
  {
    image: '/images/onboarding/slide3.svg',
    title: 'Получайте учебную помощь в нашем сообществе',
    description: 'StudHome — это не просто сервис, это комьюнити студентов, где можно задать вопрос, получить совет или найти решение.',
    bg: '#fafafa',
    ellipse: 'ellipse--slide3',
    theme: 'blue',
  },
  {
    image: '/images/onboarding/slide4.svg',
    title: 'Копите бонусы и участвуйте в программе лояльности',
    description: 'Чем активнее ты участвуешь, тем больше получаешь: бонусы, скидки и доступ к закрытым возможностям.',
    bg: '#fafafa',
    ellipse: 'ellipse--slide4',
    theme: 'light',
  },
]

const SWIPE_THRESHOLD = 50

export default function Onboarding() {
  const [step, setStep] = useState(0)
  const [animState, setAnimState] = useState('enter')
  const navigate = useNavigate()
  const { haptic } = useTelegram()
  const touchStartX = useRef(null)
  const touchStartY = useRef(null)
  const isAnimating = useRef(false)

  const slide = SLIDES[step]
  const isLast = step === SLIDES.length - 1
  const isFirst = step === 0

  useEffect(() => {
    SLIDES.forEach((s) => {
      const img = new Image()
      img.src = s.image
    })
  }, [])

  useEffect(() => {
    const t = setTimeout(() => setAnimState('visible'), 50)
    return () => clearTimeout(t)
  }, [])

  function goTo(nextStep, dir) {
    if (isAnimating.current) return
    isAnimating.current = true
    haptic('impact', 'light')

    setAnimState(dir === 'left' ? 'exit-left' : 'exit-right')

    setTimeout(() => {
      setStep(nextStep)
      setAnimState(dir === 'left' ? 'pre-enter-right' : 'pre-enter-left')

      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setAnimState('visible')
          isAnimating.current = false
        })
      })
    }, 280)
  }

  function next() {
    if (isAnimating.current) return
    if (!isLast) {
      goTo(step + 1, 'left')
    } else {
      finish()
    }
  }

  function prev() {
    if (isAnimating.current) return
    if (!isFirst) {
      goTo(step - 1, 'right')
    }
  }

  function finish() {
    if (isAnimating.current) return
    haptic('notification', 'success')
    localStorage.setItem('onboarding_done', '1')
    navigate('/', { replace: true })
  }

  function handleTouchStart(e) {
    touchStartX.current = e.touches[0].clientX
    touchStartY.current = e.touches[0].clientY
  }

  function handleTouchEnd(e) {
    if (touchStartX.current === null) return
    const deltaX = e.changedTouches[0].clientX - touchStartX.current
    const deltaY = e.changedTouches[0].clientY - touchStartY.current
    touchStartX.current = null
    touchStartY.current = null

    if (Math.abs(deltaY) > Math.abs(deltaX)) return

    if (deltaX < -SWIPE_THRESHOLD && !isLast) {
      next()
    } else if (deltaX > SWIPE_THRESHOLD && !isFirst) {
      prev()
    }
  }

  const themeClass = slide.theme === 'dark'
    ? 'onboarding--dark'
    : slide.theme === 'blue'
      ? 'onboarding--blue'
      : ''

  return (
    <div
      className={`onboarding ${themeClass}`}
      style={{ backgroundColor: slide.bg }}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      {/* iOS grab handle */}
      <div className="onboarding__handle" />

      {/* Background ellipse */}
      <div className={`onboarding__ellipse ${slide.ellipse}`} />

      {/* Skip */}
      {!isLast && (
        <button className="onboarding__skip" onClick={finish}>
          Пропустить
        </button>
      )}

      {/* Content */}
      <div className={`onboarding__content onboarding__content--${animState}`}>
        <div className="onboarding__illustration">
          <img
            src={slide.image}
            alt={slide.title}
            className="onboarding__image"
            draggable={false}
          />
        </div>

        <div className="onboarding__text">
          <h1 className="onboarding__title">{slide.title}</h1>
          <p className="onboarding__description">{slide.description}</p>
        </div>
      </div>

      {/* Footer */}
      <div className="onboarding__footer">
        <div className="onboarding__dots">
          {SLIDES.map((_, i) => (
            <div
              key={i}
              className={`onboarding__dot${i === step ? ' onboarding__dot--active' : ''}`}
            />
          ))}
        </div>

        <button className="onboarding__button" onClick={next}>
          <span className="onboarding__button-text">
            {isLast ? 'Начать' : 'Далее'}
          </span>
        </button>
      </div>
    </div>
  )
}
