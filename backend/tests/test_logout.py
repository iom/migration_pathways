import uuid
import json

def test_logout_success(client):
    test_user = {
        "username": f"TestUser_{uuid.uuid4().hex[:6]}",
        "email": f"testlogout_{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestPass123!",
        "security_question": "What is your favorite animal?",
        "security_answer": "elephant"
    }

    # Sign up
    signup_response = client.post("/api/signup", json=test_user)
    assert signup_response.status_code == 201

    # Login
    login_response = client.post("/api/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert login_response.status_code == 200

    # Extract cookie
    token_cookie = login_response.headers.get("Set-Cookie")
    assert "auth_token=" in token_cookie

    # Logout using cookie
    logout_response = client.post("/api/logout", headers={
        "Cookie": token_cookie
    })

    data = logout_response.get_json()
    assert logout_response.status_code == 200
    assert data["message"] == "Logout successful!"


def test_logout_without_token(client):
    # Directly call logout without any cookie
    response = client.post("/api/logout")
    data = response.get_json()

    assert response.status_code == 401
    assert "Token is missing" in data["error"]




