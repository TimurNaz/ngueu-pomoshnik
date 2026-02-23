export default function OnboardingScreen2() {
	return (
		<div className='onboarding-screen'>
			<div className='onboarding-screen__content'>
				{/* Иллюстрация персонажа */}
				<div className='onboarding-screen__illustration'>
					<svg viewBox='0 0 200 200' className='onboarding-screen__svg'>
						{/* Круглый фон */}
						<circle cx='100' cy='100' r='95' fill='#E8D5F2' />

						{/* Персонаж (квадратное туловище) */}
						<rect x='60' y='90' width='80' height='70' rx='20' fill='#A366CC' />

						{/* Голова */}
						<circle cx='100' cy='50' r='40' fill='#B88FD9' />

						{/* Глазки */}
						<circle cx='90' cy='45' r='5' fill='#fff' />
						<circle cx='110' cy='45' r='5' fill='#fff' />

						{/* Улыбка */}
						<path
							d='M 90 55 Q 100 65 110 55'
							stroke='#fff'
							strokeWidth='3'
							fill='none'
							strokeLinecap='round'
						/>

						{/* Руки */}
						<rect
							x='30'
							y='100'
							width='20'
							height='50'
							rx='10'
							fill='#A366CC'
						/>
						<rect
							x='150'
							y='100'
							width='20'
							height='50'
							rx='10'
							fill='#A366CC'
						/>
					</svg>
				</div>

				{/* Текст */}
				<h1 className='onboarding-screen__title'>
					Находите своих исполнителей
				</h1>
				<p className='onboarding-screen__description'>
					Выбирай специалистов под свои задачи — без лишних сложностей. У нас
					удобно, прозрачно и безопасно.
				</p>
			</div>
		</div>
	)
}
