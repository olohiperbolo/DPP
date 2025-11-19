# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from pathlib import Path

# Konfiguracja bazy danych
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ustawienie silnika bazy danych
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Tworzenie sesji
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Funkcja do uzyskiwania sesji
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
