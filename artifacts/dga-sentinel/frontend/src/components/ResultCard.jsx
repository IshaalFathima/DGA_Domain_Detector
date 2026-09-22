import './ResultCard.css'

const THRESHOLD_DISPLAY = '-0.273063'

/**
 * ResultCard — shows DGA / NO DGA verdict, Detection Strength, and threshold.
 * The ensemble score is a model decision score, NOT a probability.
 */
export default function ResultCard({ result }) {
  const isDGA = result.detection_state === 'DGA'
  const isBorderline = result.detection_state === 'BORDERLINE'
  const stateClass = isDGA ? 'dga' : isBorderline ? 'borderline' : 'safe'

  return (
    <div className={`result-card result-card--${stateClass}`}>
      {/* ---- Verdict ---------------------------------------------------- */}
      <div className="result-verdict">
        <div className={`verdict-badge verdict-badge--${stateClass}`}>
          <span className="verdict-dot" />
          {isDGA ? 'DGA DETECTED' : isBorderline ? 'BORDERLINE' : 'NO DGA DETECTED'}
        </div>
        <p className="verdict-description">
          {isDGA
            ? 'Likely algorithmically generated'
            : isBorderline
              ? 'The ensemble score is close to the detection threshold. The DGA classification is inconclusive.'
            : 'More consistent with legitimate-domain patterns'}
        </p>
      </div>

      {/* ---- Domain ----------------------------------------------------- */}
      <div className="result-domain">
        <span className="result-domain-text">{result.normalized_domain}</span>
        {result.dga_label && result.dga_label !== result.normalized_domain && (
          <span className="result-dga-label">
            label: <code>{result.dga_label}</code>
          </span>
        )}
      </div>

      {/* ---- Scores ----------------------------------------------------- */}
      <div className="result-scores">
        <div className="score-cell">
          <span className="score-label">DETECTION STRENGTH</span>
          <span className={`score-value score-value--${stateClass}`}>
            {result.ensemble_score.toFixed(4)}
          </span>
          <span className="score-note">ensemble model score</span>
        </div>
        <div className="score-divider" />
        <div className="score-cell">
          <span className="score-label">DECISION THRESHOLD</span>
          <span className="score-value score-value--neutral">{THRESHOLD_DISPLAY}</span>
          <span className="score-note">frozen — not a probability</span>
        </div>
      </div>

      {/* ---- Disclaimer ------------------------------------------------- */}
      <p className="result-disclaimer">
        DGA detection reflects similarity to algorithmically generated domain
        characteristics. It does not prove that a domain is malicious.
      </p>
    </div>
  )
}
