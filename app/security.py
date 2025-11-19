from typing import Optional
from app.db import get_db
from sqlalchemy.orm import Session
from .models import User
from passlib.context import CryptContext
from jose import jwt
import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Konfiguracja JWT
SECRET_KEY = os.getenv("SECRET_KEY", "DEV_ONLY_CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Funkcja do hashowania hasła
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Funkcja do weryfikacji hasła
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Funkcja do generowania tokenu JWT
def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject, "role": role, "iat": int(datetime.now(tz=timezone.utc).timestamp())}
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Funkcja autoryzująca użytkownika z tokenu
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowy token lub brak autoryzacji",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise credentials_exception
    return user
