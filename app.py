from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager
import csv
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ładowanie danych do bazy...")
    load_movies_to_db()
    load_links_to_db()
    load_ratings_to_db()
    load_tags_to_db()
    print("Dane załadowane!")
    yield
    print("Zamykanie aplikacji...")


app = FastAPI(lifespan=lifespan)

DATABASE_URL = "sqlite:///./movies.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"
    
    movieId = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genres = Column(String)


class Link(Base):
    __tablename__ = "links"
    
    movieId = Column(Integer, primary_key=True, index=True)
    imdbId = Column(String)
    tmdbId = Column(String, nullable=True)


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, index=True)
    movieId = Column(Integer, index=True)
    rating = Column(Float)
    timestamp = Column(Integer)


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, index=True)
    movieId = Column(Integer, index=True)
    tag = Column(String)
    timestamp = Column(Integer)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            separators=(", ", ": "),
        ).encode("utf-8")


def load_movies_to_db(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/movies.csv'):
    db = SessionLocal()
    try:
        if db.query(Movie).count() > 0:
            print("Movies już załadowane")
            return
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                movie = Movie(
                    movieId=int(row['movieId']),
                    title=row['title'],
                    genres=row['genres']
                )
                db.add(movie)
            db.commit()
            print(f"Załadowano {db.query(Movie).count()} filmów")
    except Exception as e:
        print(f"Błąd podczas ładowania movies: {e}")
        db.rollback()
    finally:
        db.close()


def load_links_to_db(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/links.csv'):
    db = SessionLocal()
    try:
        if db.query(Link).count() > 0:
            print("Links już załadowane")
            return
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                link = Link(
                    movieId=int(row['movieId']),
                    imdbId=row['imdbId'],
                    tmdbId=row['tmdbId'] if row['tmdbId'] else None
                )
                db.add(link)
            db.commit()
            print(f"Załadowano {db.query(Link).count()} linków")
    except Exception as e:
        print(f"Błąd podczas ładowania links: {e}")
        db.rollback()
    finally:
        db.close()


def load_ratings_to_db(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/ratings.csv'):
    db = SessionLocal()
    try:
        if db.query(Rating).count() > 0:
            print("Ratings już załadowane")
            return
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            batch = []
            for i, row in enumerate(reader):
                rating = Rating(
                    userId=int(row['userId']),
                    movieId=int(row['movieId']),
                    rating=float(row['rating']),
                    timestamp=int(row['timestamp'])
                )
                batch.append(rating)
                
                if len(batch) >= 1000:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
            
            if batch:
                db.bulk_save_objects(batch)
                db.commit()
            
            print(f"Załadowano {db.query(Rating).count()} ocen")
    except Exception as e:
        print(f"Błąd podczas ładowania ratings: {e}")
        db.rollback()
    finally:
        db.close()


def load_tags_to_db(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/tags.csv'):
    db = SessionLocal()
    try:
        if db.query(Tag).count() > 0:
            print("Tags już załadowane")
            return
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            batch = []
            for row in reader:
                tag = Tag(
                    userId=int(row['userId']),
                    movieId=int(row['movieId']),
                    tag=row['tag'],
                    timestamp=int(row['timestamp'])
                )
                batch.append(tag)
                
                if len(batch) >= 1000:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
            
            if batch:
                db.bulk_save_objects(batch)
                db.commit()
            
            print(f"Załadowano {db.query(Tag).count()} tagów")
    except Exception as e:
        print(f"Błąd podczas ładowania tags: {e}")
        db.rollback()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"hello": "world"}


@app.get("/movies", response_class=PrettyJSONResponse)
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).all()
    return [movie.__dict__ for movie in movies if not movie.__dict__['_sa_instance_state']]


@app.get("/links", response_class=PrettyJSONResponse)
def get_links(db: Session = Depends(get_db)):
    links = db.query(Link).all()
    return [{k: v for k, v in link.__dict__.items() if k != '_sa_instance_state'} for link in links]


@app.get("/ratings", response_class=PrettyJSONResponse)
def get_ratings(db: Session = Depends(get_db), limit: int = 100):
    ratings = db.query(Rating).limit(limit).all()
    return [{k: v for k, v in rating.__dict__.items() if k != '_sa_instance_state'} for rating in ratings]


@app.get("/tags", response_class=PrettyJSONResponse)
def get_tags(db: Session = Depends(get_db), limit: int = 100):
    tags = db.query(Tag).limit(limit).all()
    return [{k: v for k, v in tag.__dict__.items() if k != '_sa_instance_state'} for tag in tags]
