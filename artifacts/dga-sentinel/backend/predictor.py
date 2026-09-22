"""
DGA SENTINEL — Frozen ML inference pipeline.

All model artifacts are loaded ONCE at application startup via the
ModelPredictor.load() method.  No fitting, refitting, or retraining
occurs at any point during inference.

Ensemble formula (frozen):
    ensemble_score = 0.75 * robust_standardize(model1_score, frozen_stats)
                   + 0.25 * robust_standardize(model5_score, frozen_stats)

Decision threshold (frozen):
    -0.2730625331994264
"""

import logging

import joblib
import numpy as np
from scipy.sparse import hstack

from config import (
    MODEL1_SVM_PATH,
    MODEL1_VECTORIZER_PATH,
    MODEL5_SVM_PATH,
    MODEL5_VECTORIZER_PATH,
    MODEL5_SCALER_PATH,
    MODEL1_REFERENCE_MEDIAN,
    MODEL1_REFERENCE_MAD,
    MODEL5_REFERENCE_MEDIAN,
    MODEL5_REFERENCE_MAD,
    MODEL1_WEIGHT,
    MODEL5_WEIGHT,
    DECISION_THRESHOLD,
    DECISION_THRESHOLD_DISPLAY,
    STRUCTURAL_FEATURE_ORDER,
)
from domain_utils import clean_domain, extract_dga_label_v2
from feature_extractor import extract_features
from explanation import generate_observations

logger = logging.getLogger(__name__)

BORDERLINE_MARGIN: float = 0.10


def _robust_standardize_fixed(x: float, ref_median: float, ref_mad: float) -> float:
    """
    Apply fixed robust standardization using frozen reference statistics.

    The reference median and MAD are computed from the training distribution
    and MUST NOT be recalculated from inference-time inputs.
    """
    if ref_mad == 0:
        # Fallback — should not occur with properly frozen stats
        return x - ref_median
    return (x - ref_median) / (1.4826 * ref_mad)


def _get_detection_state(ensemble_score: float) -> str:
    """Return the presentation state without changing binary classification."""
    threshold_margin = ensemble_score - DECISION_THRESHOLD
    distance_from_threshold = abs(threshold_margin)

    if distance_from_threshold <= BORDERLINE_MARGIN:
        return "BORDERLINE"
    if ensemble_score >= DECISION_THRESHOLD:
        return "DGA"
    return "NOT DGA-LIKE"


class ModelPredictor:
    """
    Loads all model artifacts once and provides stateless domain prediction.
    """

    def __init__(self) -> None:
        self._loaded: bool = False
        self.model1_svm = None
        self.model1_vectorizer = None
        self.model5_svm = None
        self.model5_vectorizer = None
        self.model5_scaler = None

    def load(self) -> None:
        """Load all frozen artifacts from disk.  Call once at startup."""
        logger.info("Loading Model 1 artifacts …")
        self.model1_vectorizer = joblib.load(MODEL1_VECTORIZER_PATH)
        self.model1_svm = joblib.load(MODEL1_SVM_PATH)

        logger.info("Loading Model 5 artifacts …")
        self.model5_vectorizer = joblib.load(MODEL5_VECTORIZER_PATH)
        self.model5_scaler = joblib.load(MODEL5_SCALER_PATH)
        self.model5_svm = joblib.load(MODEL5_SVM_PATH)

        self._loaded = True
        logger.info("All model artifacts loaded successfully.")

    def predict(self, domain: str) -> dict:
        """
        Run the full frozen inference pipeline for a single domain.

        Returns a dict containing all fields required by PredictResponse.
        """
        if not self._loaded:
            raise RuntimeError("Model artifacts have not been loaded yet.")

        # ------------------------------------------------------------------ #
        # 1. Normalize domain and extract DGA label
        # ------------------------------------------------------------------ #
        normalized = clean_domain(domain)
        dga_label = extract_dga_label_v2(normalized)

        # The analysis string used by both vectorizers
        analysis_text = dga_label if dga_label else normalized

        # ------------------------------------------------------------------ #
        # 2. Extract 24 structural features
        # ------------------------------------------------------------------ #
        features = extract_features(normalized, dga_label)

        # ------------------------------------------------------------------ #
        # 3. Model 1 — Character TF-IDF + LinearSVC
        # ------------------------------------------------------------------ #
        X1 = self.model1_vectorizer.transform([analysis_text])
        model1_score: float = float(self.model1_svm.decision_function(X1)[0])

        # ------------------------------------------------------------------ #
        # 4. Model 5 — Character TF-IDF + 24 structural features + LinearSVC
        # ------------------------------------------------------------------ #
        X5_tfidf = self.model5_vectorizer.transform([analysis_text])

        struct_vec = np.array(
            [[features[f] for f in STRUCTURAL_FEATURE_ORDER]], dtype=float
        )
        struct_scaled = self.model5_scaler.transform(struct_vec)

        X5_combined = hstack([X5_tfidf, struct_scaled])
        model5_score: float = float(self.model5_svm.decision_function(X5_combined)[0])

        # ------------------------------------------------------------------ #
        # 5. Robust standardize using frozen reference statistics
        # ------------------------------------------------------------------ #
        norm1 = _robust_standardize_fixed(
            model1_score, MODEL1_REFERENCE_MEDIAN, MODEL1_REFERENCE_MAD
        )
        norm5 = _robust_standardize_fixed(
            model5_score, MODEL5_REFERENCE_MEDIAN, MODEL5_REFERENCE_MAD
        )

        # ------------------------------------------------------------------ #
        # 6. Ensemble score and classification
        # ------------------------------------------------------------------ #
        ensemble_score: float = MODEL1_WEIGHT * norm1 + MODEL5_WEIGHT * norm5
        classification: str = (
            "DGA" if ensemble_score >= DECISION_THRESHOLD else "NOT DGA-LIKE"
        )
        threshold_margin: float = ensemble_score - DECISION_THRESHOLD
        detection_state: str = _get_detection_state(ensemble_score)

        # ------------------------------------------------------------------ #
        # 7. Deterministic observations
        # ------------------------------------------------------------------ #
        observations = generate_observations(features, classification)

        return {
            "domain": domain,
            "normalized_domain": normalized,
            "dga_label": dga_label,
            "classification": classification,
            "detection_state": detection_state,
            "ensemble_score": ensemble_score,
            "threshold": DECISION_THRESHOLD,
            "threshold_margin": threshold_margin,
            "threshold_display": DECISION_THRESHOLD_DISPLAY,
            "model1_score": model1_score,
            "model1_normalized_score": norm1,
            "model5_score": model5_score,
            "model5_normalized_score": norm5,
            "features": features,
            "observations": observations,
        }


# Singleton instance — loaded once at FastAPI startup
predictor = ModelPredictor()
