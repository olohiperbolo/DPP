# app/main.py
from fastapi import FastAPI, Depends
from app.db import get_db
from app.auth_router import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix='/auth')

@app.get("/")
def root():
    return {"message": "Witaj w API filmów"}

@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    # Twoja logika dla filmów
    movies = db.query(Movie).limit(50).all()
    return movies
