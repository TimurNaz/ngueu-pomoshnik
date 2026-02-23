import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Screen1 from '../components/onboarding/Screen1'
import Screen2 from '../components/onboarding/Screen2'
import Screen3 from '../components/onboarding/Screen3'
import { useTelegram } from '../hooks/useTelegram'

const SCREENS = [Screen1, Screen2, Screen3]

export default function Onboarding() {
  const [step, setStep] = useState(0)
  const navigate = useNavigate()
  const { haptic } = useTelegram()

  function next() {
    haptic('impact', 'light')
    if (step < SCREENS.length - 1) {
      setStep((s) => s + 1)
    } else {
      finish()
    }
  }

  function finish() {
    localStorage.setItem('onboarding_done', '1')
    navigate('/', { replace: true })
  }

  const CurrentScreen = SCREENS[step]
  const isLast = step === SCREENS.length - 1

  return (
    <div className="onboarding">
      <div className="onboarding__slides">
        <CurrentScreen />
      </div>

      {/* Индикаторы */}
      <div className="onboarding__dots">
        {SCREENS.map((_, i) => (
          <div
            key={i}
            className={`onboarding__dot${i === step ? ' active' : ''}`}
            onClick={() => i < step && setStep(i)}
          />
        ))}
      </div>

      {/* Действия */}
      <div className="onboarding__actions">
        <button className="btn btn--green" onClick={next}>
          {isLast ? '🚀 Начать' : 'Далее →'}
        </button>
        {!isLast && (
          <p className="onboarding__skip" onClick={finish}>
            Пропустить
          </p>
        )}
      </div>
    </div>
  )
}
