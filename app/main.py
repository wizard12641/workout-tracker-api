"""Workout Tracker API — entrypoint.

Exposes the FastAPI application instance used by uvicorn.
"""
from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db


app = FastAPI(
    title="Workout Tracker API",
    description=(
        "A backend REST API for logging resistance training sessions, "
        "with derived analytics for one-rep-max estimation and personal-record detection."
    ),
    version="0.1.0",
)

@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)) -> JSONResponse:
    """Liveness probe used by the deployment platform.

    Returns 200 with database status "ok" when the application can reach
    Postgres. Returns 503 with "unreachable" if the database query fails.
    """
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "db": "ok"},
        )
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "db": "unreachable"},
        )