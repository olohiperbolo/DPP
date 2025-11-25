from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.auth_router import router as auth_router
from app.models import Movie, Base
from app.security import get_current_user

# Tworzenie tabel w bazie danych przy starcie
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix='/auth')

@app.get("/")
def root():
    return {"message": "Witaj w API filmów"}

@app.get("/movies")
def get_movies(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    movies = db.query(Movie).limit(50).all()
    return movies