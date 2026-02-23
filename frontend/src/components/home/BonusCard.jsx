export default function BonusCard() {
	return (
		<div className='bonus-card'>
			<div className='bonus-card__header'>
				<div>
					<p className='bonus-card__label'>Твоя карта бонусов</p>
					<p className='bonus-card__brand'>EdulpingBot</p>
				</div>
			</div>

			<div className='bonus-card__content'>
				<div className='bonus-card__amount'>500₽</div>
				<div className='bonus-card__illustration'>
					<svg viewBox='0 0 120 120' className='bonus-card__svg'>
						{/* Круг фона */}
						<circle cx='60' cy='60' r='55' fill='#fff' opacity='0.1' />

						{/* Девушка */}
						<circle cx='60' cy='35' r='20' fill='#FFE5B4' />
						{/* Волосы */}
						<path d='M 40 35 Q 40 15 60 15 Q 80 15 80 35' fill='#8B4513' />

						{/* Туловище */}
						<rect x='45' y='55' width='30' height='35' rx='8' fill='#FFE5B4' />

						{/* Сертификат */}
						<rect x='55' y='50' width='35' height='40' rx='4' fill='#B7F34A' />
						<rect x='58' y='53' width='29' height='34' rx='2' fill='#fff' />
						<line
							x1='60'
							y1='58'
							x2='80'
							y2='58'
							stroke='#B7F34A'
							strokeWidth='2'
						/>
						<line
							x1='60'
							y1='65'
							x2='80'
							y2='65'
							stroke='#ddd'
							strokeWidth='1'
						/>
						<line
							x1='60'
							y1='72'
							x2='80'
							y2='72'
							stroke='#ddd'
							strokeWidth='1'
						/>
						<circle cx='65' cy='82' r='4' fill='#B7F34A' />
					</svg>
				</div>
			</div>
		</div>
	)
}
