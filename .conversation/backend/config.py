"""
DGA SENTINEL — Frozen configuration constants.

All statistics, weights, and threshold values are taken from
ensemble_calibrated_config.json and MUST NOT be modified.
"""

import json
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
# Frozen ensemble configuration
# Source: ensemble_calibrated_config.json
# DO NOT modify — these are training-time reference statistics.
# ---------------------------------------------------------------------------

with open(ENSEMBLE_CALIBRATED_CONFIG_PATH, "r", encoding="utf-8") as _config_file:
    _AUTHORITATIVE_CONFIG = json.load(_config_file)

MODEL1_REFERENCE_MEDIAN: float = _AUTHORITATIVE_CONFIG["model_1_reference_median"]
MODEL1_REFERENCE_MAD: float = _AUTHORITATIVE_CONFIG["model_1_reference_mad"]

MODEL5_REFERENCE_MEDIAN: float = _AUTHORITATIVE_CONFIG["model_5_reference_median"]
MODEL5_REFERENCE_MAD: float = _AUTHORITATIVE_CONFIG["model_5_reference_mad"]

# ---------------------------------------------------------------------------
# Ensemble weights
# ---------------------------------------------------------------------------

MODEL1_WEIGHT: float = _AUTHORITATIVE_CONFIG["model_1_weight"]
MODEL5_WEIGHT: float = _AUTHORITATIVE_CONFIG["model_5_weight"]

# ---------------------------------------------------------------------------
# Decision threshold — exact frozen value from ensemble_calibrated_config.json
# UI may display the rounded form: -0.273063
# ---------------------------------------------------------------------------

DECISION_THRESHOLD: float = _AUTHORITATIVE_CONFIG["threshold"]
DECISION_THRESHOLD_DISPLAY: str = f"{DECISION_THRESHOLD:.6f}"

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
