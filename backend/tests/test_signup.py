import json
import uuid

def test_signup_missing_fields(client):
    # Send a POST request with empty data
    response = client.post("/api/signup", json={})
    
    # Convert to JSON
    data = response.get_json()

    # Assert the response
    assert response.status_code == 400
    assert "All fields are required" in data["error"]



def test_signup_valid_user(client):
    test_user = {
        "username": f"TestUser_{uuid.uuid4().hex[:6]}",  # Unique username
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",  # Unique email
        "password": "SecurePass123",
        "security_question": "What is your pet's name?",
        "security_answer": "fluffy"
    }

    response = client.post("/api/signup", json=test_user)
    data = response.get_json()

    assert response.status_code == 201
    assert "Signup successful" in data["message"]

def test_signup_duplicate_email(client):
    # Same user as before
    test_user = {
        "username": "TestUser",
        "email": "testuser_valid@example.com",  # Already used in previous test
        "password": "SecurePass123",
        "security_question": "What is your pet's name?",
        "security_answer": "fluffy"
    }

    response = client.post("/api/signup", json=test_user)
    data = response.get_json()

    assert response.status_code == 400
    assert "already exists" in data["error"]


def test_signup_missing_security_answer(client):
    test_user = {
        "username": "NewUser",
        "email": "newuser@example.com",
        "password": "AnotherPass123",
        "security_question": "What is your favorite color?"
        # Missing 'security_answer'
    }

    response = client.post("/api/signup", json=test_user)
    data = response.get_json()

    assert response.status_code == 400
    assert "All fields are required" in data["error"]
