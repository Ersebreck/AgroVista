import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import DATABASE_URL, SessionLocal
from app.models import Base
from app.populate_db import create_terrains_and_parcels, create_users

DB_NAME = "agrovista"
DB_USER = "usuario"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5434"


def create_database() -> None:
    """Create the AgroVista database if it doesn't exist."""
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created.")
    else:
        print(f"ℹ Database '{DB_NAME}' already exists.")
    cursor.close()
    conn.close()


def enable_postgis() -> None:
    """Enable PostGIS extension in the database."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    print("PostGIS extension enabled.")
    cursor.close()
    conn.close()


def create_tables() -> None:
    """Create all database tables."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(bind=engine)  # Optional: clean if already exists
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


def populate_data() -> None:
    """Populate the database with initial data."""
    db: Session = SessionLocal()
    owners = create_users(db)
    create_terrains_and_parcels(db, owners)
    db.close()
    print("Initial data inserted.")


if __name__ == "__main__":
    create_database()
    enable_postgis()
    create_tables()
    populate_data()


# ----------------------
# LEGACY FUNCTION NAMES (Spanish names for backwards compatibility)
# ----------------------

# Legacy function aliases
create_terrenos_y_parcelas = create_terrains_and_parcels
