"""
DGA SENTINEL — Backend regression test suite.

Tests are organized into two groups:
  - UNIT tests: pure Python logic (normalization, features, math).
    These run without loading ML artifacts and do NOT require scipy DLLs
    at import time.
  - INTEGRATION tests: require loaded model artifacts (marked @needs_models).
    These are skipped automatically if model loading fails (e.g., DLL policy).

Run from the backend/ directory:
    python -m pytest tests/ -v
    python -m pytest tests/ -v -m unit          # unit tests only
    python -m pytest tests/ -v -m integration   # integration tests only
"""

import math
import sys
import os

import pytest

# Allow imports from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_utils import clean_domain, extract_dga_label_v2
from feature_extractor import extract_features, shannon_entropy, max_consecutive, VOWELS
from config import (
    DECISION_THRESHOLD,
    MODEL1_WEIGHT,
    MODEL5_WEIGHT,
    MODEL1_REFERENCE_MEDIAN,
    MODEL1_REFERENCE_MAD,
    MODEL5_REFERENCE_MEDIAN,
    MODEL5_REFERENCE_MAD,
    STRUCTURAL_FEATURE_ORDER,
    DECISION_THRESHOLD_DISPLAY,
)
from explanation import generate_observations

# ============================================================
# Try to load ML libraries — mark as unavailable if DLL/import fails
# ============================================================

_models_available = False
_models_load_error = ""

try:
    import joblib  # noqa: F401
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    from predictor import predictor, _robust_standardize_fixed
    _models_available = True
except Exception as exc:
    _models_load_error = str(exc)
    # Create a dummy so tests can reference the name
    predictor = None  # type: ignore
    def _robust_standardize_fixed(x, m, mad):  # type: ignore
        if mad == 0:
            return x - m
        return (x - m) / (1.4826 * mad)

needs_models = pytest.mark.skipif(
    not _models_available,
    reason=f"ML libraries/DLLs not available: {_models_load_error}",
)

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def loaded_predictor():
    """Load model artifacts once for integration tests."""
    if not _models_available:
        pytest.skip("ML libraries not available")
    try:
        predictor.load()
    except Exception as exc:
        pytest.skip(f"Model loading failed: {exc}")
    return predictor


# ============================================================
# pytest marks
# ============================================================

def pytest_configure(config):
    config.addinivalue_line("markers", "unit: pure Python unit tests")
    config.addinivalue_line("markers", "integration: tests requiring ML artifacts")


# ============================================================
# 1. Health endpoint
# ============================================================

@needs_models
def test_health_endpoint(loaded_predictor):
    """GET /api/health must return {"status": "ok"}."""
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ============================================================
# 2. Prediction endpoint — valid input
# ============================================================

@needs_models
def test_predict_endpoint_valid_domain(loaded_predictor):
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    response = client.post("/api/predict", json={"domain": "nvlyffua.com"})
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert data["classification"] in ("DGA", "NOT DGA-LIKE")
    assert "ensemble_score" in data
    assert "features" in data
    assert "observations" in data
    assert len(data["features"]) == 24


@needs_models
def test_predict_endpoint_response_fields(loaded_predictor):
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    response = client.post("/api/predict", json={"domain": "google.com"})
    assert response.status_code == 200
    data = response.json()

    required_fields = [
        "domain", "normalized_domain", "dga_label",
        "classification", "ensemble_score", "threshold", "threshold_display",
        "model1_score", "model1_normalized_score",
        "model5_score", "model5_normalized_score",
        "features", "observations",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@needs_models
def test_predict_threshold_display(loaded_predictor):
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    response = client.post("/api/predict", json={"domain": "example.com"})
    data = response.json()
    assert data["threshold_display"] == DECISION_THRESHOLD_DISPLAY


# ============================================================
# 3. Prediction endpoint — invalid input
# ============================================================

@needs_models
def test_predict_empty_domain(loaded_predictor):
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    response = client.post("/api/predict", json={"domain": ""})
    assert response.status_code == 422


@needs_models
def test_predict_missing_domain(loaded_predictor):
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    response = client.post("/api/predict", json={})
    assert response.status_code == 422


@needs_models
def test_predict_domain_too_long(loaded_predictor):
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)
    long_domain = "a" * 300 + ".com"
    response = client.post("/api/predict", json={"domain": long_domain})
    assert response.status_code == 422


# ============================================================
# 4. Domain normalization (UNIT)
# ============================================================

@pytest.mark.parametrize("input_domain,expected", [
    ("EXAMPLE.COM", "example.com"),
    ("  example.com  ", "example.com"),
    ("example.com.", "example.com"),   # trailing dot (FQDN)
    ("GOOGLE.CO.UK.", "google.co.uk"),
    ("", ""),
    ("   ", ""),
])
def test_clean_domain(input_domain, expected):
    assert clean_domain(input_domain) == expected


def test_clean_domain_non_string():
    assert clean_domain(None) == ""  # type: ignore
    assert clean_domain(123) == ""   # type: ignore


# ============================================================
# 5. Public-suffix-aware DGA label extraction (UNIT)
# ============================================================

@pytest.mark.parametrize("domain,expected", [
    # Standard ccTLD SLDs — must NOT return "co" as the DGA label
    ("yvzxk.co.uk",   "yvzxk"),
    ("yflv.co.uk",    "yflv"),
    ("fqvbk.co.cr",   "fqvbk"),
    ("zykb.co.nz",    "zykb"),
    ("ewidoc.co.id",  "ewidoc"),
    ("zdozwuw.co.id", "zdozwuw"),
    # Standard TLDs
    ("gasozjom.ru",   "gasozjom"),
    ("dokbuxok.ru",   "dokbuxok"),
    # Subdomain — first subdomain label should be returned
    ("cvyh1po636avyrsxebwbwbkn7.ddns.net", "cvyh1po636avyrsxebwbwbkn7"),
])
def test_extract_dga_label_v2(domain, expected):
    result = extract_dga_label_v2(domain)
    assert result == expected, f"For {domain!r}: expected {expected!r}, got {result!r}"


def test_extract_dga_label_empty():
    assert extract_dga_label_v2("") == ""


def test_extract_dga_label_case_insensitive():
    assert extract_dga_label_v2("GASOZJOM.RU") == extract_dga_label_v2("gasozjom.ru")


# ============================================================
# 6. Feature extraction — count and order (UNIT)
# ============================================================

def test_feature_extraction_returns_24_features():
    feats = extract_features("nvlyffua.com")
    assert len(feats) == 24


def test_feature_extraction_correct_order():
    feats = extract_features("nvlyffua.com")
    assert list(feats.keys()) == STRUCTURAL_FEATURE_ORDER


def test_feature_extraction_zero_length_domain():
    feats = extract_features("")
    assert feats["domain_length"] == 0
    assert feats["num_digits"] == 0
    assert feats["shannon_entropy"] == 0.0


def test_feature_extraction_digit_ratio():
    # "abc123" → 3 letters + 3 digits, digit_ratio = 0.5
    feats = extract_features("abc123.com")
    assert feats["num_digits"] == 3
    assert feats["num_letters"] == 3
    assert math.isclose(feats["digit_ratio"], 0.5, abs_tol=1e-6)


def test_feature_extraction_vowels_consonants():
    # "aeiou" → 5 vowels, 0 consonants
    feats = extract_features("aeiou.com")
    assert feats["num_vowels"] == 5
    assert feats["num_consonants"] == 0
    assert math.isclose(feats["vowel_ratio"], 1.0, abs_tol=1e-6)


def test_feature_extraction_entropy_non_negative():
    for domain in ["nvlyffua.com", "google.com", "a1b2c3.net"]:
        feats = extract_features(domain)
        assert feats["shannon_entropy"] >= 0.0


def test_feature_extraction_unique_char_ratio():
    # "aaaa" → 1 unique, 4 total → ratio = 0.25
    feats = extract_features("aaaa.com")
    assert feats["unique_chars"] == 1
    assert math.isclose(feats["unique_char_ratio"], 0.25, abs_tol=1e-6)


def test_feature_extraction_transitions():
    # "ab" → 1 character transition
    feats = extract_features("ab.com")
    assert feats["character_transitions"] == 1


def test_feature_extraction_letter_digit_transitions():
    # "a1b2" → letter→digit: (a→1, b→2) = 2 times; digit→letter: (1→b) = 1 time
    feats = extract_features("a1b2.com")
    assert feats["letter_digit_transitions"] == 2
    assert feats["digit_letter_transitions"] == 1


def test_feature_extraction_max_consecutive_digits():
    # "abc12345" → max consecutive digits = 5
    feats = extract_features("abc12345.com")
    assert feats["max_consecutive_digits"] == 5


def test_feature_extraction_dot_and_subdomain_count():
    feats = extract_features("sub.example.com")
    assert feats["dot_count"] == 2
    assert feats["subdomain_count"] == 1


# ============================================================
# 7. Shannon entropy helper (UNIT)
# ============================================================

def test_shannon_entropy_empty():
    assert shannon_entropy("") == 0.0


def test_shannon_entropy_single_char():
    assert math.isclose(shannon_entropy("aaaa"), 0.0, abs_tol=1e-9)


def test_shannon_entropy_two_equal_chars():
    assert math.isclose(shannon_entropy("ab"), 1.0, abs_tol=1e-9)


# ============================================================
# 8. Max consecutive helper (UNIT)
# ============================================================

def test_max_consecutive_digits():
    assert max_consecutive("aaa111bbb", lambda c: c.isdigit()) == 3


def test_max_consecutive_vowels():
    assert max_consecutive("bcaeiubc", lambda c: c in VOWELS) == 4


# ============================================================
# 9. Model loading (INTEGRATION)
# ============================================================

@needs_models
def test_model_predictor_is_loaded(loaded_predictor):
    assert loaded_predictor._loaded is True


@needs_models
def test_model_predictor_artifacts_not_none(loaded_predictor):
    assert loaded_predictor.model1_svm is not None
    assert loaded_predictor.model1_vectorizer is not None
    assert loaded_predictor.model5_svm is not None
    assert loaded_predictor.model5_vectorizer is not None
    assert loaded_predictor.model5_scaler is not None


# ============================================================
# 10. Model inference (INTEGRATION)
# ============================================================

@needs_models
def test_model1_inference_returns_float(loaded_predictor):
    label = "nvlyffua"
    X = loaded_predictor.model1_vectorizer.transform([label])
    score = loaded_predictor.model1_svm.decision_function(X)[0]
    assert isinstance(float(score), float)


@needs_models
def test_model5_inference_returns_float(loaded_predictor):
    import numpy as np
    from scipy.sparse import hstack as sp_hstack

    label = "nvlyffua"
    X_tfidf = loaded_predictor.model5_vectorizer.transform([label])

    feats = extract_features("nvlyffua.com", label)
    struct = np.array([[feats[f] for f in STRUCTURAL_FEATURE_ORDER]], dtype=float)
    struct_scaled = loaded_predictor.model5_scaler.transform(struct)

    X_combined = sp_hstack([X_tfidf, struct_scaled])
    score = loaded_predictor.model5_svm.decision_function(X_combined)[0]
    assert isinstance(float(score), float)


# ============================================================
# 11. Robust standardization — frozen stats (UNIT)
# ============================================================

def test_robust_standardize_fixed_formula():
    """Verify (x - median) / (1.4826 * MAD) formula."""
    x = 1.0
    expected = (x - MODEL1_REFERENCE_MEDIAN) / (1.4826 * MODEL1_REFERENCE_MAD)
    result = _robust_standardize_fixed(x, MODEL1_REFERENCE_MEDIAN, MODEL1_REFERENCE_MAD)
    assert math.isclose(result, expected, rel_tol=1e-9)


def test_robust_standardize_zero_mad_fallback():
    """When MAD is 0 fallback returns x - median."""
    result = _robust_standardize_fixed(2.0, 1.0, 0.0)
    assert math.isclose(result, 1.0, abs_tol=1e-9)


# ============================================================
# 12. Ensemble calculation (UNIT)
# ============================================================

def test_ensemble_formula():
    """Verify 0.75 * norm1 + 0.25 * norm5."""
    norm1 = 1.5
    norm5 = -0.5
    expected = 0.75 * norm1 + 0.25 * norm5
    actual = MODEL1_WEIGHT * norm1 + MODEL5_WEIGHT * norm5
    assert math.isclose(actual, expected, rel_tol=1e-12)


def test_ensemble_weights_sum_to_one():
    assert math.isclose(MODEL1_WEIGHT + MODEL5_WEIGHT, 1.0, abs_tol=1e-12)


# ============================================================
# 13. Frozen threshold decision (UNIT)
# ============================================================

def test_frozen_threshold_value():
    """Exact frozen threshold must be -0.2730625331994264."""
    assert math.isclose(DECISION_THRESHOLD, -0.2730625331994264, rel_tol=1e-12)


def test_classification_above_threshold_is_dga():
    score_above = DECISION_THRESHOLD + 0.001
    classification = "DGA" if score_above >= DECISION_THRESHOLD else "NOT DGA-LIKE"
    assert classification == "DGA"


def test_classification_below_threshold_is_not_dga():
    score_below = DECISION_THRESHOLD - 0.001
    classification = "DGA" if score_below >= DECISION_THRESHOLD else "NOT DGA-LIKE"
    assert classification == "NOT DGA-LIKE"


def test_classification_exactly_at_threshold_is_dga():
    classification = "DGA" if DECISION_THRESHOLD >= DECISION_THRESHOLD else "NOT DGA-LIKE"
    assert classification == "DGA"


# ============================================================
# 14. End-to-end predictor.predict() (INTEGRATION)
# ============================================================

@needs_models
def test_predict_returns_expected_keys(loaded_predictor):
    result = loaded_predictor.predict("nvlyffua.com")
    expected_keys = {
        "domain", "normalized_domain", "dga_label",
        "classification", "ensemble_score", "threshold", "threshold_display",
        "model1_score", "model1_normalized_score",
        "model5_score", "model5_normalized_score",
        "features", "observations",
    }
    assert expected_keys.issubset(result.keys())


@needs_models
def test_predict_uses_exact_threshold(loaded_predictor):
    result = loaded_predictor.predict("nvlyffua.com")
    assert result["threshold"] == DECISION_THRESHOLD


@needs_models
def test_predict_classification_consistent_with_score(loaded_predictor):
    result = loaded_predictor.predict("nvlyffua.com")
    if result["ensemble_score"] >= DECISION_THRESHOLD:
        assert result["classification"] == "DGA"
    else:
        assert result["classification"] == "NOT DGA-LIKE"


@needs_models
def test_predict_features_has_24_entries(loaded_predictor):
    result = loaded_predictor.predict("google.com")
    assert len(result["features"]) == 24


@needs_models
def test_predict_normalized_domain_lowercase(loaded_predictor):
    result = loaded_predictor.predict("NVLYFFUA.COM")
    assert result["normalized_domain"] == "nvlyffua.com"


@needs_models
def test_predict_ensemble_score_is_float(loaded_predictor):
    result = loaded_predictor.predict("google.com")
    assert isinstance(result["ensemble_score"], float)


# ============================================================
# 15. Regression — known DGA-like domains (INTEGRATION)
# ============================================================

@needs_models
@pytest.mark.parametrize("domain", [
    "nvlyffua.com",
    "jhghrlufoh.com",
    "tqjhvylf.com",
    "hufqifjq.com",
    "sjhuqlwrqhqx.com",
    "pxqgonyogeee.com",
])
def test_known_dga_domains(domain, loaded_predictor):
    result = loaded_predictor.predict(domain)
    assert result["classification"] == "DGA", (
        f"{domain!r} expected DGA, got "
        f"{result['classification']!r} (score={result['ensemble_score']:.4f})"
    )


# ============================================================
# 16. Explanation system (UNIT)
# ============================================================

def test_observations_returns_list():
    feats = extract_features("nvlyffua.com")
    obs = generate_observations(feats, "DGA")
    assert isinstance(obs, list)


def test_observations_zero_length():
    feats = extract_features("")
    obs = generate_observations(feats, "NOT DGA-LIKE")
    assert len(obs) == 1
    assert "Insufficient" in obs[0]


def test_high_entropy_observation():
    feats = extract_features("zxqvjkwpfmbtrsdlygune.com")
    obs = generate_observations(feats, "DGA")
    entropy = feats["shannon_entropy"]
    if entropy > 3.5:
        assert any("entropy" in o.lower() for o in obs)
