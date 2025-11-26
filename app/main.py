import cv2 
import numpy as np
import requests
from fastapi import FastAPI, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.auth_router import router as auth_router
from app.models import Movie, Link, Rating, Tag, Base
from app.schemas import (
    MovieOut, MovieCreate, MovieUpdate,
    LinkOut, LinkCreate, LinkUpdate,
    RatingOut, RatingCreate, RatingUpdate,
    TagOut, TagCreate, TagUpdate
)
from app.security import get_current_user
from app.schemas import ImageAnalysisRequest, ImageAnalysisResponse

# Tworzenie tabel
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router, prefix='/auth')

@app.get("/")
def root():
    return {"message": "Witaj w API filmów"}

# ==========================
# MOVIES CRUD
# ==========================

@app.get("/movies", response_model=list[MovieOut])
def get_movies(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Movie).offset(skip).limit(limit).all()

@app.get("/movies/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Film nie znaleziony")
    return movie

@app.post("/movies", response_model=MovieOut, status_code=201)
def create_movie(movie_data: MovieCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_movie = Movie(title=movie_data.title, genres=movie_data.genres)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@app.put("/movies/{movie_id}", response_model=MovieOut)
def update_movie(movie_update: MovieUpdate, movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Film nie znaleziony")
    if movie_update.title: movie.title = movie_update.title
    if movie_update.genres: movie.genres = movie_update.genres
    db.commit()
    db.refresh(movie)
    return movie

@app.delete("/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Film nie znaleziony")
    db.delete(movie)
    db.commit()
    return None

# ==========================
# LINKS CRUD
# ==========================

@app.get("/links", response_model=list[LinkOut])
def get_links(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Link).offset(skip).limit(limit).all()

@app.get("/links/{movie_id}", response_model=LinkOut)
def get_link(movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link nie znaleziony")
    return link

@app.post("/links", response_model=LinkOut, status_code=201)
def create_link(link_data: LinkCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.movieId == link_data.movieId).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Film o podanym ID nie istnieje")
    
    exists = db.query(Link).filter(Link.movieId == link_data.movieId).first()
    if exists:
        raise HTTPException(status_code=409, detail="Link dla tego filmu już istnieje")

    # POPRAWKA: Używamy model_dump() zamiast dict() (Pydantic v2)
    new_link = Link(**link_data.model_dump())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@app.put("/links/{movie_id}", response_model=LinkOut)
def update_link(link_update: LinkUpdate, movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link nie znaleziony")
    
    if link_update.imdbId: link.imdbId = link_update.imdbId
    if link_update.tmdbId: link.tmdbId = link_update.tmdbId
    db.commit()
    db.refresh(link)
    return link

@app.delete("/links/{movie_id}", status_code=204)
def delete_link(movie_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link nie znaleziony")
    db.delete(link)
    db.commit()
    return None

# ==========================
# RATINGS CRUD
# ==========================

@app.get("/ratings", response_model=list[RatingOut])
def get_ratings(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Rating).offset(skip).limit(limit).all()

@app.get("/ratings/{rating_id}", response_model=RatingOut)
def get_rating(rating_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Ocena nie znaleziona")
    return rating

@app.post("/ratings", response_model=RatingOut, status_code=201)
def create_rating(rating_data: RatingCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_rating = Rating(
        userId=current_user.id,
        movieId=rating_data.movieId,
        rating=rating_data.rating,
        timestamp=rating_data.timestamp
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@app.put("/ratings/{rating_id}", response_model=RatingOut)
def update_rating(rating_update: RatingUpdate, rating_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Ocena nie znaleziona")
    
    if rating.userId != current_user.id and current_user.role != "ROLE_ADMIN":
         raise HTTPException(status_code=403, detail="Nie możesz edytować cudzej oceny")

    if rating_update.rating is not None: rating.rating = rating_update.rating
    if rating_update.timestamp is not None: rating.timestamp = rating_update.timestamp
    db.commit()
    db.refresh(rating)
    return rating

@app.delete("/ratings/{rating_id}", status_code=204)
def delete_rating(rating_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Ocena nie znaleziona")
    db.delete(rating)
    db.commit()
    return None

# ==========================
# TAGS CRUD
# ==========================

@app.get("/tags", response_model=list[TagOut])
def get_tags(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Tag).offset(skip).limit(limit).all()

@app.get("/tags/{tag_id}", response_model=TagOut)
def get_tag(tag_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag nie znaleziony")
    return tag

@app.post("/tags", response_model=TagOut, status_code=201)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_tag = Tag(
        userId=current_user.id,
        movieId=tag_data.movieId,
        tag=tag_data.tag,
        timestamp=tag_data.timestamp
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@app.put("/tags/{tag_id}", response_model=TagOut)
def update_tag(tag_update: TagUpdate, tag_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag nie znaleziony")
    
    if tag_update.tag is not None: tag.tag = tag_update.tag
    db.commit()
    db.refresh(tag)
    return tag

@app.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag nie znaleziony")
    db.delete(tag)
    db.commit()
    return None

def detect_people(image_url: str) -> int:
    """
    Pobiera obraz z URL i zlicza ludzi używając HOG Descriptor z OpenCV.
    To jest operacja blokująca CPU (symulacja ciężkiego zadania).
    """
    try:
        # 1. Pobieranie obrazu
        resp = requests.get(image_url, stream=True, timeout=10)
        resp.raise_for_status()
        
        # 2. Konwersja bajtów na obraz OpenCV
        image_array = np.asarray(bytearray(resp.content), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return 0

        # 3. Wykrywanie ludzi (HOG + SVM)
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # detectMultiScale zwraca prostokąty (boxes) i wagi
        boxes, weights = hog.detectMultiScale(image, winStride=(8,8), padding=(8,8), scale=1.05)
        
        return len(boxes)
    except Exception as e:
        print(f"Błąd analizy obrazu: {e}")
        return 0

@app.post("/analyze_img", response_model=ImageAnalysisResponse)
def analyze_image_sync(request: ImageAnalysisRequest, current_user = Depends(get_current_user)):
    """
    Endpoint synchroniczny - klient musi czekać, aż serwer pobierze i przetworzy zdjęcie.
    """
    count = detect_people(request.url)
    return {
        "person_count": count, 
        "message": "Analiza zakończona (synchronicznie)."
    }