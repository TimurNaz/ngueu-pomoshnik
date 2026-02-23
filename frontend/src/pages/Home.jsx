import { useNavigate } from 'react-router-dom'
import Card from '../components/Card'
import Section from '../components/Section'

export default function Home() {
  const navigate = useNavigate()

  return (
    <>
      <Section>
        <Card
          variant="primary"
          icon="📋"
          title="Подать заявку"
          text="Курсовые, дипломы, рефераты. Оформите заказ за пару минут."
          onClick={() => {
            // TODO: navigate('/order') когда будет страница формы
          }}
        />
      </Section>

      <Section title="Полезное">
        <Card
          variant="outline"
          icon="⏱"
          title="Этапы работы"
          text="Заявка → исполнитель → выполнение → оплата"
          small
        />
        <Card
          variant="outline"
          icon="💬"
          title="Поддержка"
          text="Вопросы? Пишите — мы на связи"
          small
        />
      </Section>
    </>
  )
}
