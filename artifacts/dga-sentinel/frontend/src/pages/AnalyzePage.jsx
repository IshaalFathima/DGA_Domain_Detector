import { useState, useCallback } from 'react'
import { analyzeDomain } from '../services/api.js'
import ResultCard from '../components/ResultCard.jsx'
import AnalysisSummary from '../components/AnalysisSummary.jsx'
import FeaturesGrid from '../components/FeaturesGrid.jsx'
import DetectionTechnology from '../components/DetectionTechnology.jsx'
import RecentAnalyses, {
  saveToRecent,
  loadRecent,
  clearRecent,
} from '../components/RecentAnalyses.jsx'
import './AnalyzePage.css'

export default function AnalyzePage() {
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState('')
  const [recent, setRecent]     = useState(() => loadRecent())

  const handleAnalyze = useCallback(async (domainOverride) => {
    const domain = (domainOverride ?? input).trim()
    if (!domain) {
      setError('Please enter a domain name.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await analyzeDomain(domain)
      setResult(data)
      saveToRecent(data)
      setRecent(loadRecent())
      if (!domainOverride) setInput(data.normalized_domain)
    } catch (err) {
      setError(
        typeof err.message === 'string'
          ? err.message
          : 'An error occurred. Please check that the backend is running.'
      )
    } finally {
      setLoading(false)
    }
  }, [input])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !loading) handleAnalyze()
  }

  const handleClear = () => {
    clearRecent()
    setRecent([])
  }

  const handleSelectRecent = (domain) => {
    setInput(domain)
    handleAnalyze(domain)
  }

  return (
    <div className="analyze-page">
      {/* ----------------------------------------------------------------- */}
      {/* Hero / Input                                                        */}
      {/* ----------------------------------------------------------------- */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-tag section-label">
              AI-Based DGA Detection in DNS Traffic
            </div>
            <h1 className="hero-heading">DOMAIN INTELLIGENCE</h1>
            <p className="hero-subtitle">
              Detect algorithmically generated domains
              using character and structural analysis.
            </p>

            <div className="search-bar">
              <input
                type="text"
                className="search-input"
                placeholder="Enter a domain  (e.g. nvlyffua.com)"
                value={input}
                onChange={e => {
                  setInput(e.target.value)
                  setError('')
                }}
                onKeyDown={handleKeyDown}
                disabled={loading}
                aria-label="Domain to analyze"
                autoComplete="off"
                spellCheck={false}
              />
              <button
                className="search-btn"
                onClick={() => handleAnalyze()}
                disabled={loading || !input.trim()}
                aria-label="Analyze domain"
              >
                {loading ? (
                  <span className="loading-spinner" aria-hidden="true" />
                ) : null}
                {loading ? 'Analyzing…' : 'ANALYZE DOMAIN'}
              </button>
            </div>

            {error && (
              <div className="search-error" role="alert">
                {error}
              </div>
            )}

            <div className="hero-hints">
              Character patterns&nbsp;&nbsp;•&nbsp;&nbsp;
              Domain structure&nbsp;&nbsp;•&nbsp;&nbsp;
              Entropy
            </div>
          </div>
        </div>
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* Results                                                             */}
      {/* ----------------------------------------------------------------- */}
      {result && (
        <div className="results-section">
          <div className="container results-container">
            <div className="results-heading-row">
              <h2 className="results-heading">DOMAIN ANALYSIS</h2>
            </div>

            <ResultCard result={result} />
            <AnalysisSummary observations={result.observations} />
            <FeaturesGrid features={result.features} />
            <DetectionTechnology result={result} />
          </div>
        </div>
      )}

      {/* ----------------------------------------------------------------- */}
      {/* Recent Analyses                                                     */}
      {/* ----------------------------------------------------------------- */}
      <div className="container recent-section">
        <RecentAnalyses
          entries={recent}
          onSelect={handleSelectRecent}
          onClear={handleClear}
        />
      </div>
    </div>
  )
}
