# tests/test_chat.py
import uuid
import openai
import pytest

def test_chat_success(client, monkeypatch):
    user = {
        "username": f"ChatUser_{uuid.uuid4().hex[:6]}",
        "email": f"chat_{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestChat123!",
        "security_question": "Favorite fruit?",
        "security_answer": "banana"
    }

    # Signup + login
    client.post("/api/signup", json=user)
    login = client.post("/api/login", json={
        "email": user["email"],
        "password": user["password"]
    })
    token_cookie = login.headers.get("Set-Cookie")

    # Monkeypatch OpenAI call
    class MockResponse:
        def __init__(self):
            self.choices = [type("obj", (object,), {"message": type("msg", (object,), {"content": "Hello! I’m your assistant."})})()]
    
    monkeypatch.setattr(openai.ChatCompletion, "create", lambda **kwargs: MockResponse())

    # Send chat message
    response = client.post("/api/chat", json={"message": "How to migrate to Canada?"}, headers={"Cookie": token_cookie})
    data = response.get_json()

    assert response.status_code == 200
    assert "text" in data
    assert "assistant" in data["sender"]

def test_chat_missing_message(client):
    # Valid user setup
    user = {
        "username": f"ChatUser_{uuid.uuid4().hex[:6]}",
        "email": f"chat_{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestChat123!",
        "security_question": "Favorite fruit?",
        "security_answer": "banana"
    }

    client.post("/api/signup", json=user)
    login = client.post("/api/login", json={
        "email": user["email"],
        "password": user["password"]
    })
    token_cookie = login.headers.get("Set-Cookie")

    response = client.post("/api/chat", json={}, headers={"Cookie": token_cookie})
    data = response.get_json()

    assert response.status_code == 400
    assert "Missing message" in data["error"]

def test_chat_unauthorized(client):
    response = client.post("/api/chat", json={"message": "Hello?"})
    data = response.get_json()

    assert response.status_code == 401
    assert "Token is missing" in data["error"]
