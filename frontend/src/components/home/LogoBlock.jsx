export default function LogoBlock() {
	return (
		<div className='logo-block'>
			<svg viewBox='0 0 200 100' className='logo-block__logo'>
				<rect
					x='20'
					y='20'
					width='160'
					height='60'
					rx='16'
					fill='#4BC8E8'
					opacity='0.1'
				/>
				<text
					x='100'
					y='65'
					textAnchor='middle'
					fontSize='48'
					fontWeight='300'
					fill='#4BC8E8'
					fontFamily="'Manrope', sans-serif"
					letterSpacing='2'
				>
					NGUEY
				</text>
			</svg>
		</div>
	)
}
