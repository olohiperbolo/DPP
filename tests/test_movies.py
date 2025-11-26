def test_create_movie(client):
    # D - weryfikacja czy po wykonaniu requestu POST dodał się nowy element
    payload = {"title": "Test Movie", "genres": "Action"}
    response = client.post("/movies", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Movie"
    assert "movieId" in data

def test_read_movies_list(client):
    # Najpierw dodajmy film
    client.post("/movies", json={"title": "Movie 1", "genres": "Drama"})
    client.post("/movies", json={"title": "Movie 2", "genres": "Comedy"})

    # A - weryfikacja czy endpoint GET zwraca tyle elementów ile jest w bazie
    response = client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_read_movie_item(client):
    # Dodajemy film
    res_create = client.post("/movies", json={"title": "Unique Movie", "genres": "Horror"})
    movie_id = res_create.json()["movieId"]

    # B - weryfikacja czy endpoint GET (po item) zwraca element o ID z bazy
    response = client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Unique Movie"

def test_read_movie_not_found(client):
    # C - weryfikacja statusu 404 dla nieistniejącego ID
    response = client.get("/movies/99999")
    assert response.status_code == 404

def test_update_movie(client):
    # Dodajemy film
    res_create = client.post("/movies", json={"title": "Old Title", "genres": "Old Genre"})
    movie_id = res_create.json()["movieId"]

    # E - weryfikacja czy po wysłaniu PUT zmiana pojawiła się w bazie
    payload = {"title": "New Title", "genres": "New Genre"}
    response = client.put(f"/movies/{movie_id}", json=payload)
    
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

    # Sprawdźmy czy GET też widzi zmianę
    get_res = client.get(f"/movies/{movie_id}")
    assert get_res.json()["title"] == "New Title"

def test_delete_movie(client):
    # Dodajemy film
    res_create = client.post("/movies", json={"title": "To Delete", "genres": "None"})
    movie_id = res_create.json()["movieId"]

    # Usuwamy
    response = client.delete(f"/movies/{movie_id}")
    assert response.status_code == 204

    # Sprawdzamy czy zniknął (powinien być 404)
    get_res = client.get(f"/movies/{movie_id}")
    assert get_res.status_code == 404