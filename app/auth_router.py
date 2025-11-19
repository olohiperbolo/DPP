from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate, UserOut, Token, LoginRequest
from .security import hash_password, verify_password, create_access_token, get_current_user
from .main import get_db

router = APIRouter()

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

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Zły login lub hasło")
    access_token = create_access_token(subject=user.username, role=user.role)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
