def test_create_tag(client):
    # Tworzymy film
    movie_res = client.post("/movies", json={"title": "Tagged Movie", "genres": "Horror"})
    movie_id = movie_res.json()["movieId"]

    # Tworzymy tag
    payload = {"movieId": movie_id, "tag": "scary"}
    response = client.post("/tags", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["tag"] == "scary"
    assert data["movieId"] == movie_id

def test_read_tags_list(client):
    response = client.get("/tags")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_tag(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    m_id = movie_res.json()["movieId"]
    tag_res = client.post("/tags", json={"movieId": m_id, "tag": "funny"})
    tag_id = tag_res.json()["id"]

    # Update
    response = client.put(f"/tags/{tag_id}", json={"tag": "hilarious"})
    assert response.status_code == 200
    assert response.json()["tag"] == "hilarious"

def test_delete_tag(client):
    # Setup
    movie_res = client.post("/movies", json={"title": "M", "genres": "G"})
    m_id = movie_res.json()["movieId"]
    tag_res = client.post("/tags", json={"movieId": m_id, "tag": "bad"})
    tag_id = tag_res.json()["id"]

    # Delete
    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 204
    
    # Verify
    get_res = client.get(f"/tags/{tag_id}")
    assert get_res.status_code == 404