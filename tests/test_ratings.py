def test_create_rating(client):
    # Tworzymy film
    movie_res = client.post("/movies", json={"title": "Rated Movie", "genres": "Action"})
    movie_id = movie_res.json()["movieId"]

    # Tworzymy ocenę
    payload = {"movieId": movie_id, "rating": 5.0}
    response = client.post("/ratings", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5.0
    assert data["movieId"] == movie_id
    assert "userId" in data # Sprawdzamy czy backend przypisał usera

def test_read_ratings_list(client):
    client.get("/ratings") # Po prostu sprawdzamy czy endpoint działa
    response = client.get("/ratings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_rating(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    m_id = movie_res.json()["movieId"]
    rate_res = client.post("/ratings", json={"movieId": m_id, "rating": 3.0})
    rating_id = rate_res.json()["id"]

    # Update
    response = client.put(f"/ratings/{rating_id}", json={"rating": 4.5})
    assert response.status_code == 200
    assert response.json()["rating"] == 4.5

def test_delete_rating(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    m_id = movie_res.json()["movieId"]
    rate_res = client.post("/ratings", json={"movieId": m_id, "rating": 3.0})
    rating_id = rate_res.json()["id"]

    # Delete
    response = client.delete(f"/ratings/{rating_id}")
    assert response.status_code == 204

    # Verify
    get_res = client.get(f"/ratings/{rating_id}")
    assert get_res.status_code == 404