export default function OnboardingScreen3() {
  return (
    <div className="onboarding-screen">
      <div className="onboarding-screen__illustration">
        <svg viewBox="0 0 200 200" className="onboarding-screen__svg">
          <circle cx="100" cy="100" r="95" fill="#D6FBE8" />
          {/* Телефон */}
          <rect x="65" y="40" width="70" height="120" rx="16" fill="#fff" stroke="#4bc8e8" strokeWidth="2" />
          <rect x="72" y="55" width="56" height="85" rx="8" fill="#f4f4f4" />
          {/* Прогресс-бар */}
          <rect x="80" y="65" width="40" height="6" rx="3" fill="#e0e0e0" />
          <rect x="80" y="65" width="28" height="6" rx="3" fill="#4bc8e8" />
          <rect x="80" y="79" width="40" height="6" rx="3" fill="#e0e0e0" />
          <rect x="80" y="79" width="14" height="6" rx="3" fill="#b7f34a" />
          {/* Монетка */}
          <circle cx="147" cy="55" r="20" fill="#b7f34a" />
          <text x="147" y="61" textAnchor="middle" fontSize="18">💸</text>
          {/* Галочка */}
          <circle cx="55" cy="140" r="16" fill="#4bc8e8" />
          <text x="55" y="146" textAnchor="middle" fontSize="14">✓</text>
        </svg>
      </div>
      <span className="onboarding-screen__tag">💳 Безопасно</span>
      <h1 className="onboarding-screen__title">Оплата только за результат</h1>
      <p className="onboarding-screen__description">
        Деньги хранятся в сервисе до принятия работы. Никакого обмана — только честная сделка.
      </p>
    </div>
  )
}
