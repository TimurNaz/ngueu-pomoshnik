import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Onboarding from './pages/Onboarding'

function App() {
	const [isLoading, setIsLoading] = useState(true)
	const [showOnboarding, setShowOnboarding] = useState(false)

	// При загрузке приложения проверяем localStorage
	useEffect(() => {
		const completed = localStorage.getItem('onboardingCompleted')
		setShowOnboarding(!completed)
		setIsLoading(false)
	}, [])

	// Пока загружается - не показываем ничего
	if (isLoading) {
		return null
	}

	return (
		<Routes>
			{showOnboarding ? (
				// Если онбординг не пройден, показываем его
				<Route path='*' element={<Onboarding />} />
			) : (
				// Если онбординг пройден, показываем приложение
				<>
					<Route path='/' element={<Layout />}>
						<Route index element={<Home />} />
					</Route>
					<Route path='*' element={<Navigate to='/' replace />} />
				</>
			)}
		</Routes>
	)
}

export default App
