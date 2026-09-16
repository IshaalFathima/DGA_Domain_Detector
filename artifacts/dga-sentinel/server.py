"""Launch the preserved FastAPI app from the artifact root."""

import os
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ARTIFACT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )