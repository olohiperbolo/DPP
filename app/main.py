from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from .models import Base, Movie, Link, Rating, Tag
from contextlib import asynccontextmanager
import csv, json
from .auth_router import router as auth_router

from .models import Base, Movie, Link, Rating, Tag

# --- Konfiguracja bazy danych ---
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Format JSON ładnie sformatowany ---
class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")


# --- Funkcje pomocnicze do ładowania CSV ---
def load_csv_to_db(model, filename: Path, db: Session):
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            obj = model(**{k: (v if v != "" else None) for k, v in row.items()})
            db.add(obj)
        db.commit()


def init_data():
    db = SessionLocal()
    if db.query(Movie).count() == 0:
        load_csv_to_db(Movie, BASE_DIR.parent / "database" / "movies.csv", db)
    if db.query(Link).count() == 0:
        load_csv_to_db(Link, BASE_DIR.parent / "database" / "links.csv", db)
    if db.query(Rating).count() == 0:
        load_csv_to_db(Rating, BASE_DIR.parent / "database" / "ratings.csv", db)
    if db.query(Tag).count() == 0:
        load_csv_to_db(Tag, BASE_DIR.parent / "database" / "tags.csv", db)
    db.close()


# --- FastAPI lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ładowanie danych CSV...")
    init_data()
    yield
    print("Zamykanie aplikacji...")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix='/auth')

# --- Endpointy ---
@app.get("/", response_class=PrettyJSONResponse)
def root():
    return {"message": "Witaj w API filmów"}

@app.get("/movies", response_class=PrettyJSONResponse)
def get_movies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        return {"error": "Brak uprawnień do przeglądania filmów"}
    movies = db.query(Movie).limit(50).all()
    return [m.__dict__ for m in movies]

@app.get("/ratings", response_class=PrettyJSONResponse)
def get_ratings(db: Session = Depends(get_db), limit: int = 100, user: User = Depends(get_current_user)):
    if user.role != "admin":
        return {"error": "Brak uprawnień do przeglądania ocen"}
    ratings = db.query(Rating).limit(limit).all()
    return [r.__dict__ for r in ratings]

@app.get("/tags", response_class=PrettyJSONResponse)
def get_tags(db: Session = Depends(get_db), limit: int = 100, user: User = Depends(get_current_user)):
    if user.role != "admin":
        return {"error": "Brak uprawnień do przeglądania tagów"}
    tags = db.query(Tag).limit(limit).all()
    return [t.__dict__ for t in tags]

@app.get("/links", response_class=PrettyJSONResponse)
def get_all_links(db: Session = Depends(get_db), limit: int = 100, user: User = Depends(get_current_user)):
    if user.role != "admin":
        return {"error": "Brak uprawnień do przeglądania linków"}
    links = db.query(Link).limit(limit).all()
    return [
        {
            "movieId": link.movieId,
            "imdbId": link.imdbId,
            "tmdbId": link.tmdbId,
        }
        for link in links
    ]
