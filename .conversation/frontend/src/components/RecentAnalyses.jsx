import './RecentAnalyses.css'

const STORAGE_KEY = 'dga_sentinel_recent'
const MAX_ENTRIES = 10

/**
 * Persist a new analysis result to localStorage.
 * Call this from the parent after a successful prediction.
 */
export function saveToRecent(result) {
  const entry = {
    domain: result.normalized_domain,
    classification: result.classification,
    ensemble_score: result.ensemble_score,
    timestamp: new Date().toISOString(),
  }

  const existing = loadRecent()
  // Deduplicate by domain — replace if already present
  const filtered = existing.filter(e => e.domain !== entry.domain)
  const updated = [entry, ...filtered].slice(0, MAX_ENTRIES)

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
  } catch {
    // localStorage quota exceeded — silent fail
  }
}

export function loadRecent() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

export function clearRecent() {
  localStorage.removeItem(STORAGE_KEY)
}

function formatTime(iso) {
  try {
    const d = new Date(iso)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) +
           ' · ' +
           d.toLocaleDateString([], { month: 'short', day: 'numeric' })
  } catch {
    return ''
  }
}

/**
 * RecentAnalyses — reads from localStorage, renders last N analyses,
 * supports click-to-re-analyze and clear-history.
 */
export default function RecentAnalyses({ entries, onSelect, onClear }) {
  if (!entries || entries.length === 0) return null

  return (
    <section className="recent card" aria-label="Recent Analyses">
      <div className="recent-header">
        <div className="section-label" style={{ margin: 0 }}>Recent Analyses</div>
        <button className="recent-clear" onClick={onClear} aria-label="Clear history">
          Clear history
        </button>
      </div>

      <div className="recent-list">
        {entries.map((entry, i) => {
          const isDGA = entry.classification === 'DGA'
          return (
            <button
              key={i}
              className="recent-item"
              onClick={() => onSelect(entry.domain)}
              aria-label={`Re-analyze ${entry.domain}`}
            >
              <span className={`recent-dot ${isDGA ? 'recent-dot--dga' : 'recent-dot--safe'}`} />
              <span className="recent-domain">{entry.domain}</span>
              <span className={`recent-badge ${isDGA ? 'recent-badge--dga' : 'recent-badge--safe'}`}>
                {isDGA ? 'DGA' : 'CLEAN'}
              </span>
              <span className="recent-score">
                {entry.ensemble_score.toFixed(3)}
              </span>
              <span className="recent-time">{formatTime(entry.timestamp)}</span>
            </button>
          )
        })}
      </div>
    </section>
  )
}
