"""One-off script: verify that the application can connect to Postgres
and create the users table.

Run from the project root with:
    python scripts/test_connection.py

Drops and recreates the users table — DEVELOPMENT ONLY.
"""

from app.db.base import Base
from app.db.session import engine
from app.models.user import User # noqa: F401


def main() -> None:
    """Test database connection and table creation."""
    print("Dropping and recreating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Done. Inspect with: docker exec -it workout-tracker-db psql -U workout -d workout_tracker -c '\\d users'")

    
if __name__ == "__main__":
    main()