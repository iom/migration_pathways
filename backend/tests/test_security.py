# tests/test_security.py
import uuid

def test_get_security_question_success(client):
    user = {
        "username": f"SecQ_{uuid.uuid4().hex[:6]}",
        "email": f"security_{uuid.uuid4().hex[:6]}@example.com",
        "password": "SecurityPass123",
        "security_question": "What is your pet’s name?",
        "security_answer": "tommy"
    }

    # Signup user
    signup = client.post("/api/signup", json=user)
    assert signup.status_code == 201

    # Get security question
    response = client.post("/api/get-security-question", json={
        "email": user["email"]
    })
    data = response.get_json()

    assert response.status_code == 200
    assert "question" in data
    assert user["security_question"] in data["question"]

def test_get_security_question_missing_email(client):
    response = client.post("/api/get-security-question", json={})
    data = response.get_json()

    assert response.status_code == 400
    assert "Email is required" in data["error"]

def test_get_security_question_user_not_found(client):
    response = client.post("/api/get-security-question", json={
        "email": "nonexistent_user@example.com"
    })
    data = response.get_json()

    assert response.status_code == 404
    assert "User not found" in data["error"]

def test_verify_security_answer_success(client):
    user = {
        "username": f"Verify_{uuid.uuid4().hex[:6]}",
        "email": f"verify_{uuid.uuid4().hex[:6]}@example.com",
        "password": "TestVerify123!",
        "security_question": "What is your dream city?",
        "security_answer": "tokyo"
    }

    # Signup
    client.post("/api/signup", json=user)

    # Verify correct answer
    response = client.post("/api/verify-security-answer", json={
        "email": user["email"],
        "security_question": user["security_question"],
        "security_answer": "tokyo"
    })

    data = response.get_json()
    assert response.status_code == 200
    assert "verified" in data["message"]

def test_verify_security_answer_incorrect(client):
    user = {
        "username": f"WrongAns_{uuid.uuid4().hex[:6]}",
        "email": f"wrongans_{uuid.uuid4().hex[:6]}@example.com",
        "password": "WrongAns123!",
        "security_question": "Favorite movie?",
        "security_answer": "inception"
    }

    client.post("/api/signup", json=user)

    # Wrong answer
    response = client.post("/api/verify-security-answer", json={
        "email": user["email"],
        "security_question": user["security_question"],
        "security_answer": "avengers"
    })

    data = response.get_json()
    assert response.status_code == 403
    assert "Incorrect" in data["error"]

def test_verify_security_answer_user_not_found(client):
    response = client.post("/api/verify-security-answer", json={
        "email": "nouser@example.com",
        "security_question": "Any?",
        "security_answer": "anything"
    })

    data = response.get_json()
    assert response.status_code == 404
    assert "User not found" in data["error"]

def test_verify_security_answer_missing_fields(client):
    response = client.post("/api/verify-security-answer", json={
        "email": "some@example.com"
        # Missing other fields
    })
    data = response.get_json()

    assert response.status_code == 400
    assert "All fields are required" in data["error"]

def test_update_password_success(client):
    user = {
        "username": f"PwdUser_{uuid.uuid4().hex[:6]}",
        "email": f"pwd_{uuid.uuid4().hex[:6]}@example.com",
        "password": "OriginalPass123!",
        "security_question": "What is your lucky number?",
        "security_answer": "9"
    }

    # Signup
    client.post("/api/signup", json=user)

    # Update password
    response = client.post("/api/update-password", json={
        "email": user["email"],
        "security_question": user["security_question"],
        "security_answer": "9",
        "new_password": "NewSecure123!"
    })

    data = response.get_json()
    assert response.status_code == 200
    assert "Password updated successfully" in data["message"]

    # Confirm login with new password
    login = client.post("/api/login", json={
        "email": user["email"],
        "password": "NewSecure123!"
    })
    assert login.status_code == 200

def test_update_password_wrong_answer(client):
    user = {
        "username": f"PwdWrong_{uuid.uuid4().hex[:6]}",
        "email": f"pwdwrong_{uuid.uuid4().hex[:6]}@example.com",
        "password": "WrongSecure123!",
        "security_question": "Favorite animal?",
        "security_answer": "lion"
    }

    client.post("/api/signup", json=user)

    response = client.post("/api/update-password", json={
        "email": user["email"],
        "security_question": user["security_question"],
        "security_answer": "tiger",
        "new_password": "NewSecure123!"
    })

    data = response.get_json()
    assert response.status_code == 403
    assert "Incorrect security answer" in data["error"]

def test_update_password_missing_fields(client):
    response = client.post("/api/update-password", json={
        "email": "abc@example.com",
        "security_question": "A",
        "security_answer": "B"
        # missing new_password
    })
    data = response.get_json()

    assert response.status_code == 400
    assert "All fields are required" in data["error"]

def test_update_password_user_not_found(client):
    response = client.post("/api/update-password", json={
        "email": "notfound@example.com",
        "security_question": "Q",
        "security_answer": "A",
        "new_password": "Secure123!"
    })
    data = response.get_json()

    assert response.status_code == 404
    assert "User not found" in data["error"]

