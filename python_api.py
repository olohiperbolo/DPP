from fastapi import FastAPI
from fastapi.responses import JSONResponse
import csv
from typing import List
import json

app = FastAPI()

class Movie:
    def __init__(self, movieId: str, title: str, genres: str):
        self.movieId = int(movieId)
        self.title = title
        self.genres = genres

class Link:
    def __init__(self, movieId: str, imdbId: str, tmdbId: str):
        self.movieId = int(movieId)
        self.imdbId = imdbId
        self.tmdbId = tmdbId if tmdbId else None

class Rating:
    def __init__(self, userId: str, movieId: str, rating: str, timestamp: str):
        self.userId = int(userId)
        self.movieId = int(movieId)
        self.rating = float(rating)
        self.timestamp = int(timestamp)

class Tag:
    def __init__(self, userId: str, movieId: str, tag: str, timestamp: str):
        self.userId = int(userId)
        self.movieId = int(movieId)
        self.tag = tag
        self.timestamp = int(timestamp)

# Funkcje pomocnicze do wczytywania danych
def load_movies(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/movies.csv') -> List[dict]:
    movies = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                movie = Movie(row['movieId'], row['title'], row['genres'])
                movies.append(movie.__dict__)
    except FileNotFoundError:
        print(f"Plik {filename} nie został znaleziony")
    return movies

def load_links(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/links.csv') -> List[dict]:
    links = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                link = Link(row['movieId'], row['imdbId'], row['tmdbId'])
                links.append(link.__dict__)
    except FileNotFoundError:
        print(f"Plik {filename} nie został znaleziony")
    return links

def load_ratings(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/ratings.csv') -> List[dict]:
    ratings = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                rating = Rating(row['userId'], row['movieId'], row['rating'], row['timestamp'])
                ratings.append(rating.__dict__)
    except FileNotFoundError:
        print(f"Plik {filename} nie został znaleziony")
    return ratings

def load_tags(filename: str = '/home/aleksanderopszala/programowanie/zadAPI/database/tags.csv') -> List[dict]:
    tags = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tag = Tag(row['userId'], row['movieId'], row['tag'], row['timestamp'])
                tags.append(tag.__dict__)
    except FileNotFoundError:
        print(f"Plik {filename} nie został znaleziony")
    return tags

# Endpointy
@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies")
def get_movies():
    movies = load_movies()
    return JSONResponse(content=movies)

@app.get("/links")
def get_links():
    return load_links()

@app.get("/ratings")
def get_ratings():
    return load_ratings()

@app.get("/tags")
def get_tags():
    return load_tags()
