# tests/test_admin.py
import uuid

def test_admin_login_missing_fields(client):
    response = client.post("/api/admin/login", json={})
    data = response.get_json()

    assert response.status_code == 400
    assert "Email and password are required" in data["error"]

def test_admin_login_user_not_found(client):
    response = client.post("/api/admin/login", json={
        "email": "notfound_admin@example.com",
        "password": "any"
    })
    data = response.get_json()

    assert response.status_code == 404
    assert "Admin not found" in data["error"]

# ❗ Note: This one only works if the admin exists in your DB already.
def test_admin_login_wrong_password(client):
    response = client.post("/api/admin/login", json={
        "email": "admin1@example.com",  # Replace with a real admin email in your DB
        "password": "wrongpassword"
    })
    data = response.get_json()

    assert response.status_code == 401
    assert "Invalid password" in data["error"]

# ✅ Optional test: only run if you have DB access
def test_admin_login_success(client):
    response = client.post("/api/admin/login", json={
        "email": "admin1@example.com",  # Replace with real
        "password": "adminpass1"        # Replace with real
    })

    assert response.status_code == 200
    assert "Set-Cookie" in response.headers


def test_admin_user_list_unauthorized(client):
    response = client.get("/api/admin/users")
    data = response.get_json()

    assert response.status_code == 401
    assert "Admin token is missing" in data["error"]

def test_admin_user_list_success(client):
    # Login as admin
    login = client.post("/api/admin/login", json={
        "email": "admin1@example.com",
        "password": "adminpass1"
    })
    assert login.status_code == 200

    admin_cookie = login.headers.get("Set-Cookie")
    assert "admin_token=" in admin_cookie

    # Call /api/admin/users
    response = client.get("/api/admin/users", headers={
        "Cookie": admin_cookie
    })
    data = response.get_json()

    assert response.status_code == 200
    assert "users" in data
    assert isinstance(data["users"], list)


def test_ban_and_unban_user_flow(client):
    # Step 1: Create a user
    import uuid
    test_user = {
        "username": f"BannedUser_{uuid.uuid4().hex[:6]}",
        "email": f"banme_{uuid.uuid4().hex[:6]}@example.com",
        "password": "Secure123!",
        "security_question": "Fav car?",
        "security_answer": "audi"
    }

    signup = client.post("/api/signup", json=test_user)
    assert signup.status_code == 201

    # Step 2: Admin login
    admin_login = client.post("/api/admin/login", json={
        "email": "admin1@example.com",
        "password": "adminpass1"
    })
    admin_cookie = admin_login.headers.get("Set-Cookie")

    # Step 3: Ban the user
    ban = client.post("/api/admin/ban_user", json={
        "email": test_user["email"]
    }, headers={"Cookie": admin_cookie})
    ban_data = ban.get_json()

    assert ban.status_code == 200
    assert f"{test_user['email']}" in ban_data["message"]

    # Step 4: Try logging in (should fail - banned)
    login = client.post("/api/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    login_data = login.get_json()
    assert login.status_code == 403
    assert "temporarily banned" in login_data["error"]

    # Step 5: Unban the user
    unban = client.post("/api/admin/unban_user", json={
        "email": test_user["email"]
    }, headers={"Cookie": admin_cookie})
    assert unban.status_code == 200

    # Step 6: Try logging in again (should work)
    login_again = client.post("/api/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert login_again.status_code == 200
