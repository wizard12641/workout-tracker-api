"""Workout Tracker API — entrypoint.

Exposes the FastAPI application instance used by uvicorn.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Workout Tracker API",
    description=(
        "A backend REST API for logging resistance training sessions, "
        "with derived analytics for one-rep-max estimation and personal-record detection."
    ),
    version="0.1.0",
)

@app.get("/health", tags=["health"])
def health() -> dict[str,str]:
    """Liveness probe used by the deployment platform.

    Returns a static OK response. A subsequent revision will also verify
    database connectivity (returns 503 if the DB is unreachable).
    """
    return {"status": "ok"}