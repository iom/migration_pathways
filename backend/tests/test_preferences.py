# tests/test_preferences.py
import uuid

def test_update_preferences_success(client):
    user = {
        "username": f"User_{uuid.uuid4().hex[:6]}",
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com",
        "password": "StrongPass123",
        "security_question": "What is your favorite color?",
        "security_answer": "blue"
    }

    # Signup
    response = client.post("/api/signup", json=user)
    assert response.status_code == 201

    # Login
    login = client.post("/api/login", json={
        "email": user["email"],
        "password": user["password"]
    })
    assert login.status_code == 200
    cookie = login.headers.get("Set-Cookie")
    assert "auth_token=" in cookie

    # Update preferences
    response = client.post("/api/preferences", json={
        "source_country": "India",
        "destination_country": "Germany"
    }, headers={
        "Cookie": cookie
    })

    data = response.get_json()
    assert response.status_code == 200
    assert "Preferences updated successfully" in data["message"]

def test_update_preferences_missing_fields(client):
    # Login first
    user = {
        "username": f"User_{uuid.uuid4().hex[:6]}",
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com",
        "password": "StrongPass123",
        "security_question": "What is your pet's name?",
        "security_answer": "milo"
    }

    client.post("/api/signup", json=user)
    login = client.post("/api/login", json={
        "email": user["email"],
        "password": user["password"]
    })
    cookie = login.headers.get("Set-Cookie")

    response = client.post("/api/preferences", json={
        "source_country": "India"
        # Missing destination_country
    }, headers={
        "Cookie": cookie
    })

    data = response.get_json()
    assert response.status_code == 400
    assert "required" in data["error"]

def test_update_preferences_unauthorized(client):
    response = client.post("/api/preferences", json={
        "source_country": "India",
        "destination_country": "Germany"
    })

    data = response.get_json()
    assert response.status_code == 401
    assert "Token is missing" in data["error"]
