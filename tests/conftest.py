import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool  # NOWE: Importujemy StaticPool
from sqlalchemy.orm import sessionmaker
from app.db import get_db
from app.main import app

# POPRAWKA: Importujemy WSZYSTKIE modele, aby SQLAlchemy wiedziało, że ma je utworzyć w bazie
from app.models import Base, User, Movie, Link, Rating, Tag
from app.security import get_current_user, get_current_admin_user
from fastapi.testclient import TestClient

# Używamy bazy w pamięci RAM (szybka i znika po testach)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # NOWE: Wymuszamy użycie jednego połączenia dla bazy w pamięci
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixtura: Przygotowanie bazy danych
@pytest.fixture()
def session():
    # Tworzymy wszystkie tabele (teraz Base zna Movie, Link itd. dzięki importom wyżej)
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
    def override_get_current_user():
        # Zwracamy obiekt User z rolą ADMIN, żeby testy przechodziły bez tokena
        return User(id=1, username="testadmin", role="ROLE_ADMIN", is_active=True)

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_user

    yield TestClient(app)
    
    # Sprzątanie nadpisań po teście
    app.dependency_overrides.clear()