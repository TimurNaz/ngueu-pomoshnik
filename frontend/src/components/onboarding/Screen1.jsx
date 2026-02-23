export default function OnboardingScreen1() {
	return (
		<div className='onboarding-screen'>
			<div className='onboarding-screen__content'>
				{/* Наклонённая карточка с логотипом */}
				<div className='onboarding-screen__hero'>
					<div className='onboarding-screen__logo-card'>
						<div className='onboarding-screen__logo-text'>НГУЭУ</div>
						<div className='onboarding-screen__logo-subtitle'>Помощник</div>
					</div>
				</div>

				{/* Основной текст */}
				<div className='onboarding-screen__text-block'>
					<h1 className='onboarding-screen__title'>Добро пожаловать!</h1>
					<p className='onboarding-screen__description'>
						Всё что нужно студентам НГУЭУ в одном месте
					</p>
				</div>
			</div>

			{/* Декоративные волны */}
			<div className='onboarding-screen__waves'>
				<svg viewBox='0 0 320 100' preserveAspectRatio='none'>
					<defs>
						<linearGradient
							id='wave-gradient'
							x1='0%'
							y1='0%'
							x2='100%'
							y2='0%'
						>
							<stop
								offset='0%'
								style={{ stopColor: '#4BC8E8', stopOpacity: 1 }}
							/>
							<stop
								offset='100%'
								style={{ stopColor: '#B7F34A', stopOpacity: 1 }}
							/>
						</linearGradient>
					</defs>
					<path
						d='M0,50 Q80,20 160,50 T320,50 L320,100 L0,100 Z'
						fill='url(#wave-gradient)'
					/>
					<path
						d='M0,60 Q80,30 160,60 T320,60 L320,100 L0,100 Z'
						fill='rgba(183, 243, 74, 0.5)'
					/>
				</svg>
			</div>
		</div>
	)
}
