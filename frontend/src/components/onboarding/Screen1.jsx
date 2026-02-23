export default function OnboardingScreen1() {
  return (
    <div className="onboarding-screen">
      <div className="onboarding-screen__illustration">
        <svg viewBox="0 0 200 200" className="onboarding-screen__svg">
          <circle cx="100" cy="100" r="95" fill="#D6F4FB" />
          {/* Диплом/документ */}
          <rect x="55" y="55" width="90" height="110" rx="12" fill="#fff" />
          <rect x="55" y="55" width="90" height="110" rx="12" fill="none" stroke="#4bc8e8" strokeWidth="2" />
          <rect x="70" y="80" width="60" height="8" rx="4" fill="#4bc8e8" opacity="0.5" />
          <rect x="70" y="96" width="45" height="6" rx="3" fill="#4bc8e8" opacity="0.3" />
          <rect x="70" y="110" width="50" height="6" rx="3" fill="#4bc8e8" opacity="0.3" />
          <rect x="70" y="124" width="38" height="6" rx="3" fill="#4bc8e8" opacity="0.3" />
          {/* Звёздочка */}
          <circle cx="145" cy="65" r="20" fill="#b7f34a" />
          <text x="145" y="70" textAnchor="middle" fontSize="18">⭐</text>
        </svg>
      </div>
      <span className="onboarding-screen__tag">🎓 НГУЭУ</span>
      <h1 className="onboarding-screen__title">Учебные работы без стресса</h1>
      <p className="onboarding-screen__description">
        Курсовые, дипломы, рефераты и лабораторные — находим проверенного исполнителя под твою задачу.
      </p>
    </div>
  )
}
