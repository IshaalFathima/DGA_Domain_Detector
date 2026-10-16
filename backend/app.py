"""
DGA SENTINEL — FastAPI application.

Endpoints:
    GET  /api/health    — liveness check
    POST /api/predict   — frozen ensemble DGA classification

Model artifacts are loaded once during application startup via the
FastAPI lifespan context manager.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from predictor import predictor
from schemas import HealthResponse, PredictRequest, PredictResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — load all artifacts once at startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DGA SENTINEL starting — loading model artifacts …")
    predictor.load()
    logger.info("Model artifacts ready. Application is live.")
    yield
    logger.info("DGA SENTINEL shutting down.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="DGA SENTINEL",
    description=(
        "AI-Based Detection of Algorithmically Generated Domains "
        "(DGA Detection) in DNS Traffic"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server and same-origin production builds
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    """Liveness check — returns ok when the models are loaded."""
    if not predictor._loaded:
        raise HTTPException(status_code=503, detail="Models not yet loaded.")
    return HealthResponse(status="ok")


@app.post("/api/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Analyze a domain string with the frozen DGA ensemble.

    The ensemble score is a model decision score, NOT a probability.
    """
    try:
        result = predictor.predict(request.domain)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PredictResponse(**result)
