import { useNavigate, useLocation } from 'react-router-dom'
import { useTelegram } from '../hooks/useTelegram'

export default function OrderResult() {
  const navigate = useNavigate()
  const location = useLocation()
  const { haptic } = useTelegram()

  const isError = location.state?.error === true
  const orderId = location.state?.orderId || null

  function handleAction() {
    haptic('impact', 'light')
    if (isError) {
      navigate('/new-order', { replace: true })
    } else {
      navigate('/', { replace: true })
    }
  }

  return (
    <div className="order-result">
      <div className="order-result__container">
        <div className="order-result__content">
          <div className={`order-result__circle ${isError ? 'order-result__circle--error' : ''}`}>
            {isError ? (
              <img src="/images/error-cross.svg" alt="" className="order-result__icon" />
            ) : (
              <img src="/images/success-check.svg" alt="" className="order-result__icon" />
            )}
          </div>

          <div className="order-result__text">
            {isError ? (
              <>
                <h1 className="order-result__title">Произошла ошибка на сервере</h1>
                <p className="order-result__sub">
                  В ближайшее время мы починим сервер чтобы обработать вашу заявку
                </p>
              </>
            ) : (
              <>
                <h1 className="order-result__title">
                  Ваша заявка {orderId && <span className="order-result__id">№{orderId}</span>} успешно отправлена
                </h1>
                <p className="order-result__sub">
                  Заявка появится у вас в истории где вы можете отслеживать её статус
                </p>
              </>
            )}
          </div>
        </div>

        <button className="order-result__btn" onClick={handleAction}>
          {isError ? 'Попробовать снова' : 'Вернуться на главную'}
        </button>
      </div>
    </div>
  )
}
