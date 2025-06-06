def test_login_missing_fields(client):
    response = client.post("/api/login", json={})
    data = response.get_json()

    assert response.status_code == 400
    assert "Email and password are required" in data["error"]


def test_login_invalid_user(client):
    response = client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "anyPassword123"
    })
    data = response.get_json()

    assert response.status_code == 404
    assert "User does not exist" in data["error"]


def test_login_wrong_password(client):
    # This assumes testuser_valid@example.com already exists from signup tests
    response = client.post("/api/login", json={
        "email": "testuser_valid@example.com",
        "password": "WrongPassword!"
    })
    data = response.get_json()

    assert response.status_code == 401
    assert "Invalid password" in data["error"]
