# DGA SENTINEL

**AI-Based Detection of Algorithmically Generated Domains (DGA Detection) in DNS Traffic**

DGA SENTINEL analyzes domain names using a frozen machine-learning ensemble
to identify character and structural patterns characteristic of algorithmically
generated domains (DGAs). The system classifies submitted domains as either
DGA-like or consistent with legitimate-domain patterns.

---

## Architecture

```
CNLA Project/
├── backend/                    # FastAPI inference server
│   ├── app.py                  # FastAPI application, /api/health, /api/predict
│   ├── predictor.py            # Frozen ensemble inference pipeline
│   ├── feature_extractor.py    # 24 structural features (frozen)
│   ├── domain_utils.py         # clean_domain + extract_dga_label_v2
│   ├── explanation.py          # Deterministic observation engine
│   ├── schemas.py              # Pydantic request/response models
│   ├── config.py               # Frozen constants (threshold, weights, stats)
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py         # Full regression test suite
├── frontend/                   # React + Vite web application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AnalyzePage.jsx
│   │   │   └── AboutPage.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   ├── AnalysisSummary.jsx
│   │   │   ├── FeaturesGrid.jsx
│   │   │   ├── DetectionTechnology.jsx
│   │   │   └── RecentAnalyses.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── models/                     # Frozen ML artifacts (read-only)
    ├── char_svm_model.joblib
    ├── char_tfidf_vectorizer.joblib
    ├── model_config.joblib
    ├── model5_char_structural.joblib
    ├── model5_tfidf_vectorizer.joblib
    ├── model5_scaler.joblib
    ├── ensemble_config.joblib
    ├── ensemble_config.json
    └── ensemble_calibrated_config.json   ← authoritative deployment config
```

---

## Model Artifact Locations

All model files must be present under `models/` relative to the project root.
The backend uses paths relative to `backend/../models/`.

**Authoritative configuration:** `ensemble_calibrated_config.json`

| Artifact | Description |
|---|---|
| `char_svm_model.joblib` | Model 1 — LinearSVC |
| `char_tfidf_vectorizer.joblib` | Model 1 — character TF-IDF vectorizer |
| `model5_char_structural.joblib` | Model 5 — LinearSVC |
| `model5_tfidf_vectorizer.joblib` | Model 5 — character TF-IDF vectorizer |
| `model5_scaler.joblib` | Model 5 — structural feature scaler |

---

## Installation

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
```

**Requirements:** Python 3.10+

### Frontend

```bash
cd frontend
npm install
```

**Requirements:** Node.js 18+

---

## Running the Application

### Start the backend

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Model artifacts are loaded once at startup. The backend will log
`"All model artifacts loaded successfully."` when ready.

### Start the frontend

In a separate terminal:

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

The Vite dev server proxies all `/api` requests to `http://localhost:8000`.

---

## API Endpoints

### `GET /api/health`

Liveness check.

```json
{"status": "ok"}
```

### `POST /api/predict`

Analyze a domain with the frozen DGA ensemble.

**Request:**
```json
{"domain": "nvlyffua.com"}
```

**Response:**
```json
{
  "domain": "nvlyffua.com",
  "normalized_domain": "nvlyffua.com",
  "dga_label": "nvlyffua",
  "classification": "DGA",
  "ensemble_score": -0.123,
  "threshold": -0.2730625331994264,
  "threshold_display": "-0.273063",
  "model1_score": 0.85,
  "model1_normalized_score": 0.23,
  "model5_score": 0.61,
  "model5_normalized_score": 0.30,
  "features": { ... 24 structural features ... },
  "observations": ["High character entropy suggests ..."]
}
```

> **Note:** `ensemble_score` is a model decision score, not a probability.

---

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

The test suite covers:
- `/api/health` and `/api/predict` endpoints
- Domain normalization (`clean_domain`)
- Public-suffix-aware DGA label extraction (`extract_dga_label_v2`)
  — including the 9 ccTLD test domains (co.uk, co.nz, co.cr, co.id, ddns.net)
- Exact 24-feature extraction and order
- Model loading
- Model 1 and Model 5 inference
- Robust standardization with frozen stats
- Ensemble formula and weights
- Frozen threshold decision
- Invalid input handling
- Regression on known DGA domains

---

## Frozen ML Checklist

The following are permanently frozen and must not be modified:

| Parameter | Value |
|---|---|
| Model 1 weight | 0.75 |
| Model 5 weight | 0.25 |
| Model 1 reference median | 0.527762486469102 |
| Model 1 reference MAD | 1.371751030955786 |
| Model 5 reference median | 0.23580731608378547 |
| Model 5 reference MAD | 1.2519861168469708 |
| Decision threshold | -0.2730625331994264 |

Source: `ensemble_calibrated_config.json`

---

## Limitations

- DGA detection does not prove that a domain is malicious.
- Some legitimate domains can appear DGA-like.
- Some sophisticated DGA-generated domains can resemble legitimate domains.
- Model performance depends on patterns represented in the training data.
- The ensemble score is not a probability or confidence percentage.
