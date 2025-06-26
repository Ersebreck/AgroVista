import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base
from app.db import DATABASE_URL, SessionLocal
from app.populate_db import create_users, create_terrenos_y_parcelas

DB_NAME = "agrovista"
DB_USER = "usuario"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5434"

def create_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Base de datos '{DB_NAME}' creada.")
    else:
        print(f"ℹ Base de datos '{DB_NAME}' ya existe.")
    cursor.close()
    conn.close()

def enable_postgis():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    print("Extensión PostGIS habilitada.")
    cursor.close()
    conn.close()

def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(bind=engine)  # Opcional: limpiar si ya existe
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")

def populate_data():
    db: Session = SessionLocal()
    propietarios = create_users(db)
    create_terrenos_y_parcelas(db, propietarios)
    db.close()
    print("Datos iniciales insertados.")

if __name__ == "__main__":
    create_database()
    enable_postgis()
    create_tables()
    populate_data()
