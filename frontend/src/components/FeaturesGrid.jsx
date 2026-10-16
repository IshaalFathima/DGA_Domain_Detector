import './FeaturesGrid.css'

/**
 * Human-readable labels for the 24 structural features.
 * API field names are preserved in data; only display labels change.
 */
const FEATURE_META = [
  { key: 'domain_length',            label: 'Domain Length',             unit: 'chars' },
  { key: 'num_digits',               label: 'Digit Count',               unit: '' },
  { key: 'digit_ratio',              label: 'Digit Ratio',               unit: '', pct: true },
  { key: 'num_letters',              label: 'Letter Count',              unit: '' },
  { key: 'num_vowels',               label: 'Vowel Count',               unit: '' },
  { key: 'num_consonants',           label: 'Consonant Count',           unit: '' },
  { key: 'vowel_ratio',              label: 'Vowel Ratio',               unit: '', pct: true },
  { key: 'consonant_ratio',          label: 'Consonant Ratio',           unit: '', pct: true },
  { key: 'num_special_chars',        label: 'Special Char Count',        unit: '' },
  { key: 'special_char_ratio',       label: 'Special Char Ratio',        unit: '', pct: true },
  { key: 'hyphen_count',             label: 'Hyphen Count',              unit: '' },
  { key: 'dot_count',                label: 'Dot Count',                 unit: '' },
  { key: 'subdomain_count',          label: 'Subdomain Count',           unit: '' },
  { key: 'unique_chars',             label: 'Unique Characters',         unit: '' },
  { key: 'unique_char_ratio',        label: 'Unique Char Ratio',         unit: '', pct: true },
  { key: 'shannon_entropy',          label: 'Shannon Entropy',           unit: 'bits' },
  { key: 'max_consecutive_digits',   label: 'Max Consec. Digits',        unit: '' },
  { key: 'max_consecutive_consonants', label: 'Max Consec. Consonants', unit: '' },
  { key: 'character_transitions',    label: 'Character Transitions',     unit: '' },
  { key: 'repeated_chars',           label: 'Repeated Characters',       unit: '' },
  { key: 'repeated_ratio',           label: 'Repeated Ratio',            unit: '', pct: true },
  { key: 'max_consecutive_vowels',   label: 'Max Consec. Vowels',        unit: '' },
  { key: 'letter_digit_transitions', label: 'Letter→Digit Transitions',  unit: '' },
  { key: 'digit_letter_transitions', label: 'Digit→Letter Transitions',  unit: '' },
]

function formatValue(value, meta) {
  if (typeof value !== 'number') return String(value)
  if (meta.pct) return `${(value * 100).toFixed(1)}%`
  if (Number.isInteger(value)) return String(value)
  return value.toFixed(4)
}

/**
 * FeaturesGrid — displays all 24 structural features in a clean grid.
 * Human-readable labels are used in the UI; API field names are unchanged.
 */
export default function FeaturesGrid({ features }) {
  return (
    <section className="features-section card" aria-label="Extracted Features">
      <div className="section-label">Extracted Features</div>
      <p className="features-note">
        24 structural features extracted from the domain label
      </p>
      <div className="features-grid">
        {FEATURE_META.map((meta) => {
          const value = features[meta.key]
          const formatted = formatValue(value, meta)
          return (
            <div className="feature-cell" key={meta.key} title={meta.key}>
              <span className="feature-label">{meta.label}</span>
              <span className="feature-value">
                {formatted}
                {meta.unit && (
                  <span className="feature-unit">{meta.unit}</span>
                )}
              </span>
              <span className="feature-key">{meta.key}</span>
            </div>
          )
        })}
      </div>
    </section>
  )
}
