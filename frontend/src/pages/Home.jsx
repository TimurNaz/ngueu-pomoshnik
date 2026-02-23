import { useState } from 'react'
import ActionCards from '../components/home/ActionCards'
import Blog from '../components/home/Blog'
import BonusCard from '../components/home/BonusCard'
import Footer from '../components/home/FooterBlocks'
import Greeting from '../components/home/Greeting'
import LogoBlock from '../components/home/LogoBlock'
import OrderHistory from '../components/home/OrderHistory'
import '../styles/home/home.css'

export default function Home() {
	const [userName] = useState('rockrizz')

	return (
		<div className='home'>
			<div className='home__container'>
				{/* Приветствие */}
				<Greeting userName={userName} />

				{/* Карта бонусов */}
				<BonusCard />

				{/* Две карточки действий */}
				<ActionCards />

				{/* История заявок */}
				<OrderHistory />

				{/* Блог */}
				<Blog />

				{/* Футер-блоки */}
				<Footer />

				{/* Логотип в конце */}
				<LogoBlock />
			</div>
		</div>
	)
}
