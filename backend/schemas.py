"""
DGA SENTINEL — Pydantic request / response schemas.
"""

from pydantic import BaseModel, field_validator, Field


class PredictRequest(BaseModel):
    domain: str = Field(..., description="Domain name to analyze")

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Domain cannot be empty.")
        if len(v) > 253:
            raise ValueError(
                "Domain exceeds maximum allowed length of 253 characters."
            )
        # Reject obviously invalid inputs (pure whitespace, control chars, etc.)
        if not any(c.isalnum() for c in v):
            raise ValueError(
                "Domain must contain at least one alphanumeric character."
            )
        return v


class PredictResponse(BaseModel):
    # Input / normalization
    domain: str
    normalized_domain: str
    dga_label: str

    # Classification
    classification: str          # "DGA" or "NOT DGA-LIKE"
    ensemble_score: float
    threshold: float
    threshold_display: str

    # Per-model raw and normalized scores
    model1_score: float
    model1_normalized_score: float
    model5_score: float
    model5_normalized_score: float

    # Structural features (all 24)
    features: dict

    # Explanation
    observations: list[str]


class HealthResponse(BaseModel):
    status: str
