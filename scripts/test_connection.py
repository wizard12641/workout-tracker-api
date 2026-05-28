"""One-off script: verify that the application can connect to Postgres.

Run from the project root with:
    python -m scripts.test_connection

Connects to the database, executes a trivial query, and prints the result.
Does NOT modify any schema or data. Schema changes are managed by Alembic.
"""


from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    print("Testing database connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        print(f"Connected. PostgreSQL version: {version}")
    
if __name__ == "__main__":
    main()