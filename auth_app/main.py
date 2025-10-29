from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import bcrypt

from database import Base, engine, SessionLocal
from users_db import get_user_by_username, create_user
from models import User

Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schematy danych
class LoginData(BaseModel):
    username: str
    password: str

class CreateUserData(BaseModel):
    username: str
    password: str
    role: str = "ROLE_USER"

# 🔐 Generowanie tokena JWT
def create_token(username: str, role: str):
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# 🔑 Weryfikacja tokena
def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoint logowania
@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user or not bcrypt.checkpw(data.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.username, user.role)
    return {"access_token": token, "token_type": "bearer"}

# Endpoint dodawania użytkownika (tylko admin)
@app.post("/users")
def add_user(data: CreateUserData, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    payload = verify_token(token)
    if payload.get("role") != "ROLE_ADMIN":
        raise HTTPException(status_code=403, detail="Access forbidden")

    if get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="User already exists")

    user = create_user(db, data.username, data.password, data.role)
    return {"message": f"User {user.username} created"}

# Endpoint do pobrania danych użytkownika z tokena
@app.get("/user_details")
def user_details(token: str = Depends(verify_token)):
    return {"username": token["sub"], "role": token["role"]}
