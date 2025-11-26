import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import get_db
from app.main import app
from app.models import Base, User
from app.security import get_current_user, get_current_admin_user
from fastapi.testclient import TestClient

# Używamy bazy w pamięci RAM (szybka i znika po testach)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixtura: Przygotowanie bazy danych
@pytest.fixture()
def session():
    # Tworzymy tabele
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Usuwamy tabele po testach
        Base.metadata.drop_all(bind=engine)

# Fixtura: Klient testowy (udaje przeglądarkę)
@pytest.fixture()
def client(session):
    # Nadpisujemy zależność get_db, żeby używała naszej testowej bazy
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    # Nadpisujemy autoryzację - udajemy, że jesteśmy zalogowani jako Admin
    # Dzięki temu testy CRUD nie będą wołać o token!
    def override_get_current_user():
        return User(id=1, username="testadmin", role="ROLE_ADMIN")

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_user

    yield TestClient(app)