import { useState } from 'react'

const FAQ_DATA = [
  {
    id: 'process',
    icon: '⚙️',
    name: 'Как работает сервис',
    questions: [
      {
        q: 'Как подать заявку?',
        a: 'Нажмите «Новая заявка», выберите тип работы, укажите тему и требования. Администратор подберёт исполнителя и сообщит цену.',
      },
      {
        q: 'Сколько времени занимает поиск исполнителя?',
        a: 'Обычно от 1 до 4 часов в рабочее время. В срочных случаях — быстрее. Вы получите уведомление в Telegram.',
      },
      {
        q: 'Могу ли я выбрать конкретного исполнителя?',
        a: 'Пока нет — мы сами подбираем исполнителя исходя из вашей дисциплины, преподавателя и срочности. Это гарантирует лучшее соответствие.',
      },
    ],
  },
  {
    id: 'payment',
    icon: '💳',
    name: 'Оплата и гарантии',
    questions: [
      {
        q: 'Как происходит оплата?',
        a: 'Деньги замораживаются через ЮKassa до принятия работы. После вашего подтверждения средства поступают исполнителю. Никакого риска!',
      },
      {
        q: 'Что если работа меня не устроит?',
        a: 'Вы можете запросить правки — первые 2 итерации бесплатны. Если работа не выполнена или полностью не соответствует требованиям, деньги возвращаются.',
      },
      {
        q: 'Какой размер комиссии сервиса?',
        a: 'Сервис удерживает 10% от суммы сделки. Это покрывает гарантии, поддержку и подбор исполнителей.',
      },
    ],
  },
  {
    id: 'safety',
    icon: '🔒',
    name: 'Безопасность и анонимность',
    questions: [
      {
        q: 'Мои данные в безопасности?',
        a: 'Да. Мы не передаём ваш Telegram-аккаунт или контакты исполнителю. Вся коммуникация происходит через сервис.',
      },
      {
        q: 'Узнает ли университет?',
        a: 'Мы работаем полностью анонимно. Ни клиент, ни исполнитель не раскрывают личные данные — только ник в Telegram. Ваша работа — ваше дело.',
      },
    ],
  },
  {
    id: 'works',
    icon: '📚',
    name: 'Виды работ',
    questions: [
      {
        q: 'Какие работы вы выполняете?',
        a: 'Курсовые, дипломы (ВКР), рефераты, контрольные, лабораторные, отчёты по практике, презентации, и многое другое для НГУЭУ.',
      },
      {
        q: 'Берётесь ли за срочные заказы?',
        a: 'Да, включая заказы с дедлайном 24-48 часов. Срочность влияет на цену — её обсудит исполнитель.',
      },
    ],
  },
  {
    id: 'quality',
    icon: '⭐',
    name: 'Качество работ',
    questions: [
      {
        q: 'Кто выполняет работы?',
        a: 'Только студенты и выпускники НГУЭУ, знающие требования кафедр и стандарты оформления. Все исполнители проходят проверку.',
      },
      {
        q: 'Гарантируете ли вы антиплагиат?',
        a: 'Да, если вы указали требуемый процент в заявке. Исполнитель несёт ответственность за соответствие работы заявленным требованиям.',
      },
    ],
  },
]

export default function FAQ() {
  const [openCategory, setOpenCategory] = useState(null)
  const [openItem, setOpenItem] = useState(null)

  function toggleCategory(id) {
    setOpenCategory((c) => (c === id ? null : id))
    setOpenItem(null)
  }

  function toggleItem(key) {
    setOpenItem((i) => (i === key ? null : key))
  }

  return (
    <div className="faq-page">
      <div className="faq-page__container">
        {/* Hero */}
        <div className="faq-hero">
          <div className="faq-hero__icon">💬</div>
          <h1 className="faq-hero__title">Частые вопросы</h1>
          <p className="faq-hero__sub">
            Всё, что нужно знать о работе с НГУЭУ/Помощник
          </p>
        </div>

        {/* Категории */}
        <div className="faq-categories">
          <p className="faq-section-label">Категории</p>
          {FAQ_DATA.map((cat) => (
            <div
              key={cat.id}
              className={`faq-category${openCategory === cat.id ? ' open' : ''}`}
            >
              <button
                className="faq-category__trigger"
                onClick={() => toggleCategory(cat.id)}
              >
                <div className="faq-category__icon">{cat.icon}</div>
                <div className="faq-category__info">
                  <p className="faq-category__name">{cat.name}</p>
                  <p className="faq-category__count">
                    {cat.questions.length} вопроса
                  </p>
                </div>
                <span className="faq-category__chevron">▼</span>
              </button>

              {openCategory === cat.id && (
                <div className="faq-items">
                  {cat.questions.map((item, i) => {
                    const key = `${cat.id}-${i}`
                    const isOpen = openItem === key
                    return (
                      <div
                        key={key}
                        className={`faq-item${isOpen ? ' open' : ''}`}
                      >
                        <button
                          className="faq-item__question"
                          onClick={() => toggleItem(key)}
                        >
                          <span className="faq-item__q-text">{item.q}</span>
                          <span className="faq-item__chevron">▼</span>
                        </button>
                        {isOpen && (
                          <div className="faq-item__answer">{item.a}</div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Контакт — в стиле action-card--light с главной */}
        <div className="faq-contact">
          <span className="faq-contact__icon">🎧</span>
          <h2 className="faq-contact__title">Не нашли ответ?</h2>
          <p className="faq-contact__sub">
            Напишите нам — ответим быстро и поможем разобраться в любой ситуации.
          </p>
          <button
            className="faq-contact__btn"
            onClick={() => window.open('https://t.me/zachetlearning/13', '_blank')}
          >
            💬 Написать в поддержку
          </button>
        </div>
      </div>
    </div>
  )
}
