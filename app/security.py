from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
from app.db import get_db
import bcrypt  # Używamy bezpośrednio bcrypt
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Konfiguracja JWT
SECRET_KEY = os.getenv("SECRET_KEY", "DEV_ONLY_CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Funkcja do hashowania hasła (bez passlib)
def hash_password(password: str) -> str:
    # Konwertujemy hasło na bajty i generujemy sól
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    # Hashujemy i zwracamy jako string (dekodujemy z bajtów)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

# Funkcja do weryfikacji hasła (bez passlib)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Konwertujemy oba na bajty, bo bcrypt tego wymaga
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

# Funkcja do generowania tokenu JWT
def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject, "role": role, "iat": datetime.now(timezone.utc)}
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
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

# Funkcja sprawdzająca czy użytkownik to ADMIN
def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ROLE_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień administratora"
        )
    return current_user