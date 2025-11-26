def test_create_link(client):
    # Najpierw tworzymy film, bo link musi być przypisany do filmu
    movie_res = client.post("/movies", json={"title": "Link Test Movie", "genres": "Drama"})
    movie_id = movie_res.json()["movieId"]

    # Teraz tworzymy link
    payload = {"movieId": movie_id, "imdbId": "tt1234567", "tmdbId": "12345"}
    response = client.post("/links", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["imdbId"] == "tt1234567"
    assert data["movieId"] == movie_id

def test_create_link_movie_not_found(client):
    # Próba dodania linku do nieistniejącego filmu
    payload = {"movieId": 99999, "imdbId": "tt1234567"}
    response = client.post("/links", json=payload)
    assert response.status_code == 404

def test_read_link(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    movie_id = movie_res.json()["movieId"]
    client.post("/links", json={"movieId": movie_id, "imdbId": "tt999", "tmdbId": "999"})

    # Test GET
    response = client.get(f"/links/{movie_id}")
    assert response.status_code == 200
    assert response.json()["imdbId"] == "tt999"

def test_update_link(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    movie_id = movie_res.json()["movieId"]
    client.post("/links", json={"movieId": movie_id, "imdbId": "old", "tmdbId": "old"})

    # Test PUT
    payload = {"imdbId": "new_imdb"}
    response = client.put(f"/links/{movie_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["imdbId"] == "new_imdb"
    # Sprawdzamy czy drugie pole zostało stare (nie powinno się zmienić, bo nie wysłaliśmy go)
    assert response.json()["tmdbId"] == "old"

def test_delete_link(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    movie_id = movie_res.json()["movieId"]
    client.post("/links", json={"movieId": movie_id, "imdbId": "del", "tmdbId": "del"})

    # Test DELETE
    response = client.delete(f"/links/{movie_id}")
    assert response.status_code == 204

    # Weryfikacja
    get_res = client.get(f"/links/{movie_id}")
    assert get_res.status_code == 404