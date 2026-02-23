export default function OnboardingScreen4() {
	return (
		<div className='onboarding-screen'>
			<div className='onboarding-screen__content'>
				{/* Иллюстрация прогресса */}
				<div className='onboarding-screen__illustration'>
					<svg viewBox='0 0 200 200' className='onboarding-screen__svg'>
						{/* Круглый фон */}
						<circle cx='100' cy='100' r='95' fill='#FFF3E8' />

						{/* Вертикальная линия процесса */}
						<line
							x1='100'
							y1='40'
							x2='100'
							y2='160'
							stroke='#DDD'
							strokeWidth='2'
						/>

						{/* Чекпоинт 1 - выполнен */}
						<circle cx='100' cy='60' r='12' fill='#B7F34A' />
						<text
							x='100'
							y='67'
							textAnchor='middle'
							fontSize='16'
							fill='#fff'
							fontWeight='bold'
						>
							✓
						</text>

						{/* Чекпоинт 2 - выполняется */}
						<circle cx='100' cy='100' r='12' fill='#4BC8E8' />
						<text
							x='100'
							y='107'
							textAnchor='middle'
							fontSize='14'
							fill='#fff'
							fontWeight='bold'
						>
							⟳
						</text>

						{/* Чекпоинт 3 - ожидает */}
						<circle cx='100' cy='140' r='12' fill='#E8E8E8' />
						<text x='100' y='147' textAnchor='middle' fontSize='14' fill='#999'>
							○
						</text>

						{/* Лейблы */}
						<text x='130' y='65' fontSize='11' fill='#666'>
							Заявка
						</text>
						<text x='130' y='105' fontSize='11' fill='#666'>
							Исполнение
						</text>
						<text x='130' y='145' fontSize='11' fill='#999'>
							Готово
						</text>
					</svg>
				</div>

				{/* Текст */}
				<h1 className='onboarding-screen__title'>Контролируйте процесс</h1>
				<p className='onboarding-screen__description'>
					Следите за выполнением задачи и получайте уведомления в реальном
					времени.
				</p>
			</div>
		</div>
	)
}
