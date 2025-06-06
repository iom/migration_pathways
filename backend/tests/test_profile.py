import uuid

def test_get_profile_ok(client):
    # Step 1: Register a user
    test_user = {
        "username": f"ProfileUser_{uuid.uuid4().hex[:6]}",
        "email": f"profile_{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestPass123!",
        "security_question": "Favorite food?",
        "security_answer": "pizza"
    }

    signup = client.post("/api/signup", json=test_user)
    assert signup.status_code == 201

    # Step 2: Login and get auth_token
    login = client.post("/api/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert login.status_code == 200
    token_cookie = login.headers.get("Set-Cookie")
    assert token_cookie and "auth_token=" in token_cookie

    # Step 3: Call /api/profile with auth_token
    profile = client.get("/api/profile", headers={
        "Cookie": token_cookie
    })
    data = profile.get_json()

    assert profile.status_code == 200
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "message" in data
    assert "conversation" in data


def test_get_profile_unauthenticated(client):
    # No token
    response = client.get("/api/profile")
    data = response.get_json()

    assert response.status_code == 401
    assert "Token is missing" in data["error"]


