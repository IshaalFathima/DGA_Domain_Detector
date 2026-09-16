import './AnalysisSummary.css'

/**
 * AnalysisSummary — displays deterministic observations based on
 * actual extracted feature values.  Only observations from the backend
 * (based on real feature values) are shown.
 */
export default function AnalysisSummary({ observations }) {
  return (
    <section className="analysis-summary card" aria-label="Analysis Summary">
      <div className="section-label">Analysis Summary</div>

      {observations && observations.length > 0 ? (
        <ul className="obs-list">
          {observations.map((obs, i) => (
            <li key={i} className="obs-item">
              <span className="obs-bullet">›</span>
              <span className="obs-text">{obs}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="obs-empty">
          No significant DGA-like character patterns were detected in this domain.
        </p>
      )}
    </section>
  )
}
