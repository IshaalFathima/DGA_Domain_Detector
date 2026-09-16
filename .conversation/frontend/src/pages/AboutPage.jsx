import './AboutPage.css'

export default function AboutPage() {
  return (
    <div className="about-page">
      <div className="container about-container">

        {/* ---------------------------------------------------------------- */}
        {/* Page header                                                       */}
        {/* ---------------------------------------------------------------- */}
        <div className="about-header">
          <div className="section-label">About</div>
          <h1 className="about-title">DGA SENTINEL</h1>
          <p className="about-tagline">
            AI-Based Detection of Algorithmically Generated Domains (DGA Detection)
            in DNS Traffic
          </p>
        </div>

        {/* ---------------------------------------------------------------- */}
        {/* Project Overview                                                  */}
        {/* ---------------------------------------------------------------- */}
        <section className="about-section card" aria-labelledby="overview-heading">
          <div className="section-label" id="overview-heading">Project Overview</div>
          <p>
            Algorithmically generated domains (DGAs) are used by malware to
            communicate with command-and-control (C2) infrastructure. DGA
            algorithms generate large numbers of pseudo-random domain names,
            allowing malware to rotate through domains and evade static
            blocklists.
          </p>
          <p>
            DGA SENTINEL analyzes domain names using machine-learning models
            that have been trained to recognize the character-level and
            structural patterns characteristic of algorithmically generated
            strings. The system classifies a submitted domain as either
            DGA-like or consistent with legitimate-domain patterns.
          </p>
          <p>
            Detection does not require a DNS lookup. The classifier operates
            entirely on the domain string itself.
          </p>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Detection Approach                                                */}
        {/* ---------------------------------------------------------------- */}
        <section className="about-section card" aria-labelledby="approach-heading">
          <div className="section-label" id="approach-heading">Detection Approach</div>

          <div className="approach-grid">
            <div className="approach-item">
              <div className="approach-icon">①</div>
              <div>
                <div className="approach-title">Character-Level TF-IDF</div>
                <p className="approach-desc">
                  Character n-gram TF-IDF vectorization transforms domain
                  labels into high-dimensional character sequence features.
                  This captures patterns in letter arrangements that differ
                  between algorithmically generated and human-readable domains.
                </p>
              </div>
            </div>

            <div className="approach-item">
              <div className="approach-icon">②</div>
              <div>
                <div className="approach-title">Structural Domain Features</div>
                <p className="approach-desc">
                  24 structural features are computed from each domain label,
                  including character entropy, digit ratio, vowel ratio, consonant
                  density, character transition counts, and consecutive-run
                  lengths. These capture statistical properties that are
                  distributed differently between DGA and legitimate domains.
                </p>
              </div>
            </div>

            <div className="approach-item">
              <div className="approach-icon">③</div>
              <div>
                <div className="approach-title">Ensemble Classification</div>
                <p className="approach-desc">
                  Two LinearSVC classifiers are combined in a weighted ensemble.
                  Before combining, each model's decision score is normalized
                  using robust statistics (median and MAD) computed from the
                  training distribution. The final ensemble score is compared
                  against a frozen decision threshold.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Model Information                                                 */}
        {/* ---------------------------------------------------------------- */}
        <section className="about-section card" aria-labelledby="model-heading">
          <div className="section-label" id="model-heading">Model Information</div>

          <div className="model-info-grid">
            <div className="model-info-card">
              <div className="mi-header">
                <span className="mi-tag">MODEL 1</span>
                <span className="mi-weight">75% weight</span>
              </div>
              <div className="mi-name">Character-Level TF-IDF + LinearSVC</div>
              <ul className="mi-details">
                <li>Analyzer: character n-grams, range (2–5)</li>
                <li>Max features: 300,000</li>
                <li>Classifier: LinearSVC, C=1.0, class-balanced</li>
              </ul>
            </div>

            <div className="model-info-card">
              <div className="mi-header">
                <span className="mi-tag">MODEL 5</span>
                <span className="mi-weight">25% weight</span>
              </div>
              <div className="mi-name">
                Character-Level TF-IDF + Structural Features + LinearSVC
              </div>
              <ul className="mi-details">
                <li>Analyzer: character n-grams, range (1–5)</li>
                <li>Max features: 300,000</li>
                <li>24 structural features, standardized with a frozen scaler</li>
                <li>Combined feature matrix fed to LinearSVC</li>
              </ul>
            </div>
          </div>

          <div className="ensemble-formula">
            <div className="section-label" style={{ marginBottom: '8px' }}>
              Final Ensemble
            </div>
            <code className="formula-code">
              ensemble_score = 0.75 × normalized_model1_score
              &nbsp;&nbsp;+&nbsp;&nbsp;
              0.25 × normalized_model5_score
            </code>
            <p className="formula-note">
              Decision threshold:&nbsp;
              <code>-0.273063</code>&nbsp;
              (frozen — derived from ensemble_calibrated_config.json)
            </p>
            <p className="formula-note">
              The ensemble score is a model decision score,&nbsp;
              <strong>not a probability</strong>.
            </p>
          </div>
        </section>

        {/* ---------------------------------------------------------------- */}
        {/* Limitations                                                       */}
        {/* ---------------------------------------------------------------- */}
        <section className="about-section card limitations" aria-labelledby="limits-heading">
          <div className="section-label" id="limits-heading">Limitations</div>

          <ul className="limitations-list">
            <li>
              <span className="lim-bullet">!</span>
              DGA detection does not prove that a domain is malicious. A
              DGA classification indicates that the domain exhibits
              algorithmically generated character patterns — not that it
              is actively used for malicious purposes.
            </li>
            <li>
              <span className="lim-bullet">!</span>
              Some legitimate domains can appear DGA-like. Short, random-seeming
              domain names registered by humans may produce DGA-positive
              classifications.
            </li>
            <li>
              <span className="lim-bullet">!</span>
              Some sophisticated DGA-generated domains can resemble legitimate
              domains, particularly dictionary-based DGAs.
            </li>
            <li>
              <span className="lim-bullet">!</span>
              Model performance depends on patterns represented in the training
              data. Novel DGA families may not be recognized.
            </li>
            <li>
              <span className="lim-bullet">!</span>
              The ensemble score is not a probability or a confidence
              percentage. It is a model decision score derived from
              LinearSVC decision functions.
            </li>
          </ul>
        </section>

      </div>
    </div>
  )
}
