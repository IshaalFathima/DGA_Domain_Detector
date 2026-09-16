import { useState } from 'react'
import './DetectionTechnology.css'

/**
 * DetectionTechnology — shows Model 1 (75%) and Model 5 (25%) info.
 * Optionally expands to show raw model decision scores.
 * Scores are clearly labeled as model decision scores, not probabilities.
 */
export default function DetectionTechnology({ result }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <section className="det-tech card" aria-label="Detection Technology">
      <div className="section-label">Detection Technology</div>

      <div className="model-cards">
        {/* Model 1 */}
        <div className="model-card">
          <div className="model-header">
            <span className="model-number">MODEL 1</span>
            <span className="model-weight">75%</span>
          </div>
          <div className="model-name">Character Analysis</div>
          <div className="model-desc">
            Character-level TF-IDF + LinearSVC
          </div>
          <div className="model-bar-track">
            <div className="model-bar" style={{ width: '75%' }} />
          </div>
        </div>

        {/* Model 5 */}
        <div className="model-card">
          <div className="model-header">
            <span className="model-number">MODEL 5</span>
            <span className="model-weight">25%</span>
          </div>
          <div className="model-name">Character + Structural Analysis</div>
          <div className="model-desc">
            Character-level TF-IDF + 24 structural features + LinearSVC
          </div>
          <div className="model-bar-track">
            <div className="model-bar" style={{ width: '25%' }} />
          </div>
        </div>
      </div>

      {/* Technical scores — expandable */}
      {result && (
        <div className="tech-expand">
          <button
            className="tech-toggle"
            onClick={() => setExpanded(v => !v)}
            aria-expanded={expanded}
          >
            <span>{expanded ? '▾' : '›'}</span>
            Technical scores
          </button>

          {expanded && (
            <div className="tech-scores">
              <div className="tech-row">
                <span className="tech-key">Model 1 decision score</span>
                <code className="tech-val">{result.model1_score.toFixed(6)}</code>
              </div>
              <div className="tech-row">
                <span className="tech-key">Model 1 normalized score</span>
                <code className="tech-val">{result.model1_normalized_score.toFixed(6)}</code>
              </div>
              <div className="tech-row">
                <span className="tech-key">Model 5 decision score</span>
                <code className="tech-val">{result.model5_score.toFixed(6)}</code>
              </div>
              <div className="tech-row">
                <span className="tech-key">Model 5 normalized score</span>
                <code className="tech-val">{result.model5_normalized_score.toFixed(6)}</code>
              </div>
              <div className="tech-row tech-row--total">
                <span className="tech-key">
                  Ensemble (0.75 × M1 + 0.25 × M5)
                </span>
                <code className="tech-val">{result.ensemble_score.toFixed(6)}</code>
              </div>
              <p className="tech-note">
                These are model decision scores, not probabilities or confidence percentages.
              </p>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
