import { useRef } from 'react'

export default function Blog() {
	const scrollContainer = useRef(null)

	const articles = [
		{
			id: 1,

			image: '🌞',
		},
		{
			id: 2,

			image: '🚀',
		},
		{
			id: 3,

			image: '⭐',
		},
	]

	return (
		<div className='blog'>
			<div className='blog__header'>
				<h2 className='blog__title'>Наш блог</h2>
				<button className='blog__all-button'>Все</button>
			</div>

			<div className='blog__scroll' ref={scrollContainer}>
				<div className='blog__container'>
					{articles.map(article => (
						<div key={article.id} className='blog-card'>
							<div className='blog-card__image-wrapper'>
								<div className='blog-card__image'>{article.image}</div>
								<div className='blog-card__overlay' />
							</div>
							<div className='blog-card__content'>
								<p className='blog-card__title'>{article.title}</p>
							</div>
						</div>
					))}
				</div>
			</div>
		</div>
	)
}
