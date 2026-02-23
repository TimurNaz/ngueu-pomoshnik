/**
 * Секция с опциональным заголовком.
 */
export default function Section({ title, children }) {
  return (
    <section className="section">
      {title && <h3 className="section__title">{title}</h3>}
      {children}
    </section>
  )
}
