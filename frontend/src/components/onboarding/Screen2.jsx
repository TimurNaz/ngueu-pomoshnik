export default function OnboardingScreen2() {
  return (
    <div className="onboarding-screen">
      <div className="onboarding-screen__illustration">
        <svg viewBox="0 0 200 200" className="onboarding-screen__svg">
          <circle cx="100" cy="100" r="95" fill="#E8D5F2" />
          <rect x="60" y="90" width="80" height="70" rx="20" fill="#A366CC" />
          <circle cx="100" cy="52" r="38" fill="#B88FD9" />
          <circle cx="90" cy="48" r="5" fill="#fff" />
          <circle cx="110" cy="48" r="5" fill="#fff" />
          <circle cx="91" cy="49" r="2" fill="#333" />
          <circle cx="111" cy="49" r="2" fill="#333" />
          <path d="M 90 58 Q 100 67 110 58" stroke="#fff" strokeWidth="3" fill="none" strokeLinecap="round" />
          <rect x="30" y="100" width="22" height="48" rx="11" fill="#A366CC" />
          <rect x="148" y="100" width="22" height="48" rx="11" fill="#A366CC" />
          {/* Кружки-чеки рядом */}
          <circle cx="40" cy="65" r="14" fill="#b7f34a" />
          <text x="40" y="70" textAnchor="middle" fontSize="14">✓</text>
          <circle cx="158" cy="65" r="14" fill="#4bc8e8" />
          <text x="158" y="70" textAnchor="middle" fontSize="12">👍</text>
        </svg>
      </div>
      <span className="onboarding-screen__tag">✅ Проверенные</span>
      <h1 className="onboarding-screen__title">Находите своих исполнителей</h1>
      <p className="onboarding-screen__description">
        Только студенты НГУЭУ, знающие твоих преподавателей и стандарты кафедры. Анонимно и безопасно.
      </p>
    </div>
  )
}
