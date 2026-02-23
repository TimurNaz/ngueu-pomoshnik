import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import OnboardingScreen1 from '../components/onboarding/Screen1'
import OnboardingScreen2 from '../components/onboarding/Screen2'
import OnboardingScreen3 from '../components/onboarding/Screen3'
import OnboardingScreen4 from '../components/onboarding/Screen4'
import '../styles/onboarding/onboarding.css'

export default function Onboarding() {
	const navigate = useNavigate()
	const [currentScreen, setCurrentScreen] = useState(0)

	const screens = [
		<OnboardingScreen1 key={1} />,
		<OnboardingScreen2 key={2} />,
		<OnboardingScreen3 key={3} />,
		<OnboardingScreen4 key={4} />,
	]

	const handleNext = () => {
		if (currentScreen < screens.length - 1) {
			setCurrentScreen(currentScreen + 1)
		} else {
			// Сохраняем флаг, что онбординг пройден
			localStorage.setItem('onboardingCompleted', 'true')
			// Перезагружаем приложение для активации нового маршрута
			window.location.href = '/'
		}
	}

	const handleSkip = () => {
		// Сохраняем флаг при пропуске
		localStorage.setItem('onboardingCompleted', 'true')
		// Перезагружаем приложение для активации нового маршрута
		window.location.href = '/'
	}

	return (
		<div className='onboarding'>
			<div className='onboarding__container'>
				{screens[currentScreen]}

				{/* Индикаторы */}
				<div className='onboarding__indicators'>
					{screens.map((_, index) => (
						<div
							key={index}
							className={`onboarding__indicator ${
								index === currentScreen ? 'onboarding__indicator--active' : ''
							}`}
							aria-label={`Экран ${index + 1}`}
						/>
					))}
				</div>

				{/* Кнопки */}
				<div className='onboarding__controls'>
					{currentScreen < screens.length - 1 && (
						<button className='onboarding__skip' onClick={handleSkip}>
							Пропустить
						</button>
					)}
					<button className='onboarding__button' onClick={handleNext}>
						{currentScreen === screens.length - 1 ? 'Начать' : 'Далее'}
					</button>
				</div>
			</div>
		</div>
	)
}
