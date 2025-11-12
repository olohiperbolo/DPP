from sqlalchemy import Column, Integer, String, Float, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

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


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("username", name="uq_user_username"),)

    