from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserOut, Token
from app.security import hash_password, verify_password, create_access_token, get_current_user, get_current_admin_user
from app.db import get_db

router = APIRouter()

# Zadanie 2, 4 i 6: Endpoint POST /users dostępny tylko dla ROLE_ADMIN
@router.post("/users", response_model=UserOut, status_code=201)
def create_new_user(payload: UserCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=409, detail="Użytkownik już istnieje")
    
    user = User(
        username=payload.username, 
        password_hash=hash_password(payload.password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Publiczna rejestracja (pomocnicza)
"""
@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=409, detail="Użytkownik już istnieje")
    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
"""

# POPRAWKA: Używamy OAuth2PasswordRequestForm zamiast LoginRequest (JSON),
# aby przycisk "Authorize" w Swaggerze działał poprawnie.
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger wysyła login w polu 'username' i hasło w 'password'
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Zły login lub hasło")
    
    access_token = create_access_token(subject=user.username, role=user.role)
    return {"access_token": access_token, "token_type": "bearer"}

# Zadanie 7: Endpoint /user_details
@router.get("/user_details", response_model=UserOut)
def get_user_details(user: User = Depends(get_current_user)):
    return user