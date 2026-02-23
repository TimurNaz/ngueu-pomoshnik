export default function Greeting({ userName }) {
	return (
		<div className='greeting'>
			<h1 className='greeting__title'>Привет, {userName}!</h1>
			<div className='greeting__avatar'>
				<div className='greeting__avatar-inner'>
					<span>👤</span>
				</div>
			</div>
		</div>
	)
}
