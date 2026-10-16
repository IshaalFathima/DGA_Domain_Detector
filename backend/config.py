"""
DGA SENTINEL — Frozen configuration constants.

All statistics, weights, and threshold values are taken from
ensemble_calibrated_config.json and MUST NOT be modified.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL1_SVM_PATH = os.path.join(MODELS_DIR, "char_svm_model.joblib")
MODEL1_VECTORIZER_PATH = os.path.join(MODELS_DIR, "char_tfidf_vectorizer.joblib")
MODEL1_CONFIG_PATH = os.path.join(MODELS_DIR, "model_config.joblib")

MODEL5_SVM_PATH = os.path.join(MODELS_DIR, "model5_char_structural.joblib")
MODEL5_VECTORIZER_PATH = os.path.join(MODELS_DIR, "model5_tfidf_vectorizer.joblib")
MODEL5_SCALER_PATH = os.path.join(MODELS_DIR, "model5_scaler.joblib")

ENSEMBLE_CALIBRATED_CONFIG_PATH = os.path.join(
    MODELS_DIR, "ensemble_calibrated_config.json"
)

# ---------------------------------------------------------------------------
# Frozen ensemble normalization statistics
# Source: ensemble_calibrated_config.json
# DO NOT modify — these are training-time reference statistics.
# ---------------------------------------------------------------------------

MODEL1_REFERENCE_MEDIAN: float = 0.527762486469102
MODEL1_REFERENCE_MAD: float = 1.371751030955786

MODEL5_REFERENCE_MEDIAN: float = 0.23580731608378547
MODEL5_REFERENCE_MAD: float = 1.2519861168469708

# ---------------------------------------------------------------------------
# Ensemble weights
# ---------------------------------------------------------------------------

MODEL1_WEIGHT: float = 0.75
MODEL5_WEIGHT: float = 0.25

# ---------------------------------------------------------------------------
# Decision threshold — exact frozen value from ensemble_calibrated_config.json
# UI may display the rounded form: -0.273063
# ---------------------------------------------------------------------------

DECISION_THRESHOLD: float = -0.2730625331994264
DECISION_THRESHOLD_DISPLAY: str = "-0.273063"

# ---------------------------------------------------------------------------
# Exact structural feature order for Model 5 — MUST NOT change
# ---------------------------------------------------------------------------

STRUCTURAL_FEATURE_ORDER: list[str] = [
    "domain_length",
    "num_digits",
    "digit_ratio",
    "num_letters",
    "num_vowels",
    "num_consonants",
    "vowel_ratio",
    "consonant_ratio",
    "num_special_chars",
    "special_char_ratio",
    "hyphen_count",
    "dot_count",
    "subdomain_count",
    "unique_chars",
    "unique_char_ratio",
    "shannon_entropy",
    "max_consecutive_digits",
    "max_consecutive_consonants",
    "character_transitions",
    "repeated_chars",
    "repeated_ratio",
    "max_consecutive_vowels",
    "letter_digit_transitions",
    "digit_letter_transitions",
]

# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

MAX_DOMAIN_LENGTH: int = 253
MIN_DOMAIN_LENGTH: int = 1
