export default function FooterBlocks() {
	return (
		<div className='footer-blocks'>
			<div className='footer-grid'>
				{/* Содержание */}
				<div className='footer-card'>
					<h3 className='footer-card__title'>Содержание</h3>
					<ul className='footer-card__list'>
						<li>
							<a href='#about'>О нас</a>
						</li>
						<li>
							<a href='#news'>Новости</a>
						</li>
						<li>
							<a href='#terms'>Условия</a>
						</li>
						<li>
							<a href='#jobs'>Вакансии</a>
						</li>
					</ul>
				</div>

				{/* Ресурсы */}
				<div className='footer-card'>
					<h3 className='footer-card__title'>Ресурсы</h3>
					<ul className='footer-card__list'>
						<li>
							<a href='#blog'>Блог</a>
						</li>
						<li>
							<a href='#reviews'>Отзывы</a>
						</li>
						<li>
							<a href='#faq'>FAQ</a>
						</li>
						<li>
							<a href='#support'>Поддержка</a>
						</li>
					</ul>
				</div>

				{/* Компания */}
				<div className='footer-card'>
					<h3 className='footer-card__title'>Компания</h3>
					<ul className='footer-card__list'>
						<li>
							<a href='#career'>Карьера</a>
						</li>
						<li>
							<a href='#partnership'>Партнёрство</a>
						</li>
						<li>
							<a href='#press'>Пресса</a>
						</li>
						<li>
							<a href='#privacy'>Конфиденциальность</a>
						</li>
					</ul>
				</div>

				{/* Контакты */}
				<div className='footer-card footer-card--contacts'>
					<h3 className='footer-card__title'>Контакты</h3>
					<div className='footer-card__contacts'>
						<a
							href='https://t.me/ngueu_pomoshnik'
							className='footer-contact-btn footer-contact-btn--tg'
							title='Telegram'
						>
							TG
						</a>
						<a
							href='https://vk.com'
							className='footer-contact-btn footer-contact-btn--vk'
							title='VK'
						>
							VK
						</a>
						<a
							href='mailto:hello@ngueu.bot'
							className='footer-contact-btn footer-contact-btn--email'
							title='Email'
						>
							✉
						</a>
					</div>
					<p className='footer-card__copyright'>© 2025 НГУЭУ Помощник</p>
				</div>
			</div>
		</div>
	)
}
