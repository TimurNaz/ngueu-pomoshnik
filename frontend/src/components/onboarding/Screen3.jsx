export default function OnboardingScreen3() {
	return (
		<div className='onboarding-screen'>
			<div className='onboarding-screen__content'>
				{/* Иллюстрация оплаты */}
				<div className='onboarding-screen__illustration'>
					<svg viewBox='0 0 200 200' className='onboarding-screen__svg'>
						{/* Круглый фон */}
						<circle cx='100' cy='100' r='95' fill='#E8F5E8' />

						{/* Кошелек (синий) */}
						<rect
							x='50'
							y='70'
							width='100'
							height='70'
							rx='15'
							fill='#4BC8E8'
						/>

						{/* Темная полоса сверху кошелька */}
						<rect
							x='50'
							y='70'
							width='100'
							height='20'
							rx='15'
							fill='#2FA8D4'
						/>

						{/* Монеты внутри */}
						<circle cx='75' cy='110' r='18' fill='#B7F34A' />
						<circle cx='100' cy='115' r='20' fill='#FFD700' />
						<circle cx='125' cy='110' r='18' fill='#B7F34A' />

						{/* Замок на кошельке */}
						<g transform='translate(90, 80)'>
							<rect
								x='5'
								y='0'
								width='10'
								height='12'
								fill='none'
								stroke='#fff'
								strokeWidth='1.5'
								rx='2'
							/>
							<circle cx='10' cy='8' r='2' fill='#fff' />
						</g>
					</svg>
				</div>

				{/* Текст */}
				<h1 className='onboarding-screen__title'>Безопасная оплата</h1>
				<p className='onboarding-screen__description'>
					Оплачивайте только после согласования стоимости и подтверждения
					условий.
				</p>
			</div>
		</div>
	)
}
