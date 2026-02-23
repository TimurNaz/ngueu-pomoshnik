export default function OrderHistory() {
	const orders = [
		{ id: 1, date: '23 февр.', title: 'Курсовая', amount: '4000₽', icon: '📄' },
		{
			id: 2,
			date: '20 февр.',
			title: 'Учебная практика',
			amount: '2000₽',
			icon: '📋',
		},
		{
			id: 3,
			date: '18 февр.',
			title: 'Производственная практика',
			amount: '3000₽',
			icon: '📊',
		},
		{ id: 4, date: '15 февр.', title: 'Реферат', amount: '1500₽', icon: '📝' },
	]

	return (
		<div className='order-history'>
			<h2 className='order-history__title'>История заявок</h2>

			<div className='order-list'>
				{orders.map(order => (
					<div key={order.id} className='order-item'>
						<div className='order-item__icon'>{order.icon}</div>
						<div className='order-item__content'>
							<p className='order-item__date'>{order.date}</p>
							<p className='order-item__name'>{order.title}</p>
						</div>
						<div className='order-item__amount'>{order.amount}</div>
					</div>
				))}
			</div>

			<button className='order-history__button'>Подробнее</button>
		</div>
	)
}
