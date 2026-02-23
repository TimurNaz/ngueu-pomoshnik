export default function ActionCards() {
	return (
		<div className='action-cards'>
			{/* Подать заявку */}
			<div className='action-card'>
				<div className='action-card__illustration'>
					<svg viewBox='0 0 100 100' className='action-card__svg'>
						{/* Документы */}
						<rect
							x='20'
							y='20'
							width='35'
							height='50'
							rx='4'
							fill='#E8D5F2'
							stroke='#A366CC'
							strokeWidth='2'
						/>
						<line
							x1='25'
							y1='30'
							x2='50'
							y2='30'
							stroke='#A366CC'
							strokeWidth='1.5'
						/>
						<line
							x1='25'
							y1='40'
							x2='50'
							y2='40'
							stroke='#A366CC'
							strokeWidth='1.5'
						/>
						<line
							x1='25'
							y1='50'
							x2='45'
							y2='50'
							stroke='#A366CC'
							strokeWidth='1.5'
						/>

						<rect
							x='35'
							y='35'
							width='35'
							height='50'
							rx='4'
							fill='#E8D5F2'
							opacity='0.7'
							stroke='#A366CC'
							strokeWidth='2'
						/>
						<line
							x1='40'
							y1='45'
							x2='65'
							y2='45'
							stroke='#A366CC'
							strokeWidth='1.5'
						/>
						<line
							x1='40'
							y1='55'
							x2='65'
							y2='55'
							stroke='#A366CC'
							strokeWidth='1.5'
						/>
					</svg>
				</div>
				<h3 className='action-card__title'>Подать заявку</h3>
				<button className='action-card__button'>
					<svg width='16' height='16' viewBox='0 0 16 16' fill='none'>
						<path d='M6 2L14 8L6 14V2Z' fill='currentColor' />
					</svg>
				</button>
			</div>

			{/* Правила */}
			<div className='action-card'>
				<div className='action-card__illustration'>
					<svg viewBox='0 0 100 100' className='action-card__svg'>
						{/* Лупа */}
						<circle
							cx='45'
							cy='45'
							r='25'
							fill='none'
							stroke='#4BC8E8'
							strokeWidth='3'
						/>
						<line
							x1='65'
							y1='65'
							x2='78'
							y2='78'
							stroke='#4BC8E8'
							strokeWidth='3'
							strokeLinecap='round'
						/>
						{/* Вопрос */}
						<text
							x='45'
							y='55'
							textAnchor='middle'
							fontSize='28'
							fill='#4BC8E8'
							fontWeight='bold'
						>
							?
						</text>
					</svg>
				</div>
				<h3 className='action-card__title'>Правила</h3>
				<button className='action-card__button'>
					<svg width='16' height='16' viewBox='0 0 16 16' fill='none'>
						<path d='M6 2L14 8L6 14V2Z' fill='currentColor' />
					</svg>
				</button>
			</div>
		</div>
	)
}
