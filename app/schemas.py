from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# --- IMAGE ANALYSIS SCHEMAS ---
class ImageAnalysisRequest(BaseModel):
    url: str = Field(..., description="URL do zdjęcia publicznie dostępnego w Internecie")

class ImageAnalysisResponse(BaseModel):
    person_count: int
    message: str

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    
    # Nowy sposób konfiguracji w Pydantic v2
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- MOVIE SCHEMAS ---
class MovieBase(BaseModel):
    title: str = Field(min_length=1)
    genres: str = Field(default="(no genres listed)")

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genres: Optional[str] = None

class MovieOut(MovieBase):
    movieId: int
    model_config = ConfigDict(from_attributes=True)

# --- LINK SCHEMAS ---
class LinkBase(BaseModel):
    imdbId: str
    tmdbId: Optional[str] = None

class LinkCreate(LinkBase):
    movieId: int

class LinkUpdate(BaseModel):
    imdbId: Optional[str] = None
    tmdbId: Optional[str] = None

class LinkOut(LinkBase):
    movieId: int
    model_config = ConfigDict(from_attributes=True)

# --- RATING SCHEMAS ---
class RatingBase(BaseModel):
    rating: float
    timestamp: Optional[int] = None

class RatingCreate(RatingBase):
    movieId: int

class RatingUpdate(BaseModel):
    rating: Optional[float] = None
    timestamp: Optional[int] = None

class RatingOut(RatingBase):
    id: int
    userId: int
    movieId: int
    model_config = ConfigDict(from_attributes=True)

# --- TAG SCHEMAS ---
class TagBase(BaseModel):
    tag: str
    timestamp: Optional[int] = None

class TagCreate(TagBase):
    movieId: int

class TagUpdate(BaseModel):
    tag: Optional[str] = None

class TagOut(TagBase):
    id: int
    userId: int
    movieId: int
    model_config = ConfigDict(from_attributes=True)