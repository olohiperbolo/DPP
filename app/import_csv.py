import csv
import sqlite3
import os

# Konfiguracja ścieżek
DB_PATH = 'app/database.db'
CSV_FOLDER = 'database'  # Zakładam, że folder z CSV nazywa się 'database' i jest w głównym katalogu

def import_movies(cursor):
    path = os.path.join(CSV_FOLDER, 'movies.csv')
    if not os.path.exists(path):
        print(f"Brak pliku: {path}")
        return

    print("Importowanie filmów...")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        movies_to_insert = []
        for row in reader:
            # movieId, title, genres
            movies_to_insert.append((
                row['movieId'],
                row['title'],
                row['genres']
            ))
        
        # Używamy executemany dla szybkości
        cursor.executemany(
            'INSERT OR IGNORE INTO movies (movieId, title, genres) VALUES (?, ?, ?)',
            movies_to_insert
        )
        print(f"Zaimportowano {len(movies_to_insert)} filmów.")

def import_links(cursor):
    path = os.path.join(CSV_FOLDER, 'links.csv')
    if not os.path.exists(path):
        print(f"Brak pliku: {path}")
        return

    print("Importowanie linków...")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        links_to_insert = []
        for row in reader:
            # movieId, imdbId, tmdbId
            links_to_insert.append((
                row['movieId'],
                row['imdbId'],
                row['tmdbId']
            ))
        
        cursor.executemany(
            'INSERT OR IGNORE INTO links (movieId, imdbId, tmdbId) VALUES (?, ?, ?)',
            links_to_insert
        )
        print(f"Zaimportowano {len(links_to_insert)} linków.")

def import_tags(cursor):
    path = os.path.join(CSV_FOLDER, 'tags.csv')
    if not os.path.exists(path):
        print(f"Brak pliku: {path}")
        return

    print("Importowanie tagów...")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        tags_to_insert = []
        # Uwaga: Tagi w CSV zazwyczaj mają 'userId'. 
        # Ponieważ nasza baza jest nowa, możemy nie mieć użytkowników o takich ID.
        # Dla uproszczenia przypiszemy wszystkie tagi do admina (ID=1) lub zachowamy oryginalne ID,
        # ale wtedy tabela users musi być pusta lub pozwalać na brak klucza obcego (SQLite domyślnie pozwala).
        
        for row in reader:
            # userId, movieId, tag, timestamp
            tags_to_insert.append((
                # row['userId'], # Możemy użyć oryginalnego userId
                1, # LUB przypisać wszystko do Admina (bezpieczniej, jeśli nie importujemy users)
                row['movieId'],
                row['tag'],
                row['timestamp']
            ))
        
        cursor.executemany(
            'INSERT OR IGNORE INTO tags (userId, movieId, tag, timestamp) VALUES (?, ?, ?, ?)',
            tags_to_insert
        )
        print(f"Zaimportowano {len(tags_to_insert)} tagów.")

def import_ratings(cursor):
    path = os.path.join(CSV_FOLDER, 'ratings.csv')
    if not os.path.exists(path):
        print(f"Brak pliku: {path}")
        return

    print("Importowanie ocen (może to chwilę potrwać)...")
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ratings_to_insert = []
        
        # Ogranicznik: jeśli plik ratings.csv jest gigantyczny (miliony rekordów),
        # warto wczytać tylko np. pierwsze 10 000, żeby nie "zabić" bazy SQLite.
        LIMIT = 50000 
        count = 0
        
        for row in reader:
            if count >= LIMIT:
                break
            ratings_to_insert.append((
                # row['userId'], 
                1, # Przypisujemy do Admina (ID=1) dla uproszczenia
                row['movieId'],
                row['rating'],
                row['timestamp']
            ))
            count += 1
        
        cursor.executemany(
            'INSERT OR IGNORE INTO ratings (userId, movieId, rating, timestamp) VALUES (?, ?, ?, ?)',
            ratings_to_insert
        )
        print(f"Zaimportowano {len(ratings_to_insert)} ocen.")

def main():
    if not os.path.exists(DB_PATH):
        print("Błąd: Nie znaleziono bazy danych. Uruchom najpierw serwer uvicorn, aby utworzył pustą bazę.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        import_movies(cursor)
        import_links(cursor)
        import_tags(cursor)
        import_ratings(cursor)
        conn.commit()
        print("\nSUKCES! Dane zostały zaimportowane.")
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()