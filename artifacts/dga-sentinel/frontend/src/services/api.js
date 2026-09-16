/**
 * DGA SENTINEL — API service layer.
 * All ML inference is performed by the backend. The frontend never
 * computes ensemble scores or applies thresholds itself.
 */

const BASE_URL = '/api'

/**
 * @param {string} domain
 * @returns {Promise<object>} PredictResponse
 */
export async function analyzeDomain(domain) {
  const response = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ domain }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    const detail = errorData.detail || `HTTP ${response.status}`
    throw new Error(detail)
  }

  return response.json()
}

/**
 * @returns {Promise<object>} HealthResponse
 */
export async function getHealth() {
  const response = await fetch(`${BASE_URL}/health`)
  if (!response.ok) throw new Error(`Health check failed: HTTP ${response.status}`)
  return response.json()
}
