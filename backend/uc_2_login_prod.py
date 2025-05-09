from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from sqlalchemy import create_engine, text

import urllib.parse
from dotenv import load_dotenv
import os
from chat_rag import session_contexts
from db_config import engine 


active_logins = {}  

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
from chat_rag import chat_blueprint 
app.register_blueprint(chat_blueprint)

db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
                
encoded_password = urllib.parse.quote_plus(db_password)
    
connection_string = f"postgresql://{db_username}:{encoded_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("admin_token")

        if not token:
            return jsonify({"error": "Admin token is missing"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if data.get("role") != "admin":
                return jsonify({"error": "Invalid admin token"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Admin token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid admin token'}), 401

        return f(*args, **kwargs)
    return decorated


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('auth_token')

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            email = data.get("email")

            with engine.connect() as connection:
                result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {'email': data['email']})
                user = result.fetchone()

            if not user:
                return jsonify({'error': 'User does not exist!'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication error: {str(e)}'}), 500

        return f(email,*args, **kwargs)
    return decorated

@app.route('/')
def welcome():
    return "Route checking - Server is running"

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "Username, Email, and Password are required."}), 400

    hashed_password = generate_password_hash(password)

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT active FROM users WHERE email = :email"), {'email': email}
            )
            existing_user = result.fetchone()

            if existing_user:
                if existing_user[0]:  # active == True
                    return jsonify({"error": "User with this email already exists. Please log in."}), 400
                else:
                    return jsonify({"error": "This account is banned. Please contact admin."}), 403

            # result = connection.execute(
            #     text("SELECT 1 FROM users WHERE email = :email"), {'email': email}
            # )
            # existing_user = result.fetchone()

            # if existing_user:
            #     return jsonify({"error": "User with this email already exists. Please log in."}), 400
           
            connection.execute(
                text("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)"),
                {'username': name, 'email': email, 'password': hashed_password}
            )
            connection.commit()  

        return jsonify({"message": "Signup successful! Please log in."}), 201

    except Exception as e:
        print(f"Signup error: {str(e)}") 
        return jsonify({"error": "An error occurred while signing up. Please try again later."}), 500
    
# Login API
@app.route('/api/login', methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        if active_logins.get(email):
            return jsonify({"error": "User already logged in from another session!"}), 403

        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {'email': email})
            user = result.fetchone()

        if not user:
            return jsonify({"error": "User does not exist!"}), 404

        if not check_password_hash(user[2], password):
            return jsonify({"error": "Invalid password!"}), 401

        if not user[4]:  # active column
            return jsonify({"error": "User is temporarily banned. Please contact admin."}), 403


        token = jwt.encode({
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        response = make_response(jsonify({"message": "Login successful!", "token": token}))
        response.set_cookie(
            "auth_token", token,
            httponly=True,
            samesite="Lax",
            max_age=1800
        )
        active_logins[email] = True

        return response

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route('/api/logout', methods=["POST"])
@token_required
def logout(email):  
    session_contexts.pop(email, None)

    active_logins.pop(email, None)

    response = make_response(jsonify({"message": "Logout successful!"}))
    response.set_cookie("auth_token", "", expires=0)

    return response


@app.route('/api/profile', methods=['GET'])
@token_required
def profile(email):
    token = request.cookies.get('auth_token')

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        email = data['email']

        with engine.connect() as connection:
            result = connection.execute(text("SELECT username, email FROM users WHERE email = :email"), {'email': email})
            user = result.fetchone()

        if user:
            
            conversation = session_contexts.get(email, [])
            formatted_messages = [
                {
                    "sender": "user" if msg["role"] == "user" else "assistant",
                    "text": msg["content"]
                }
                for msg in conversation
            ]
            return jsonify({
                "username": user[0],
                "email": user[1],
                "conversation": formatted_messages,  
                "message": "User profile fetched successfully."
            }), 200
        else:
            return jsonify({"error": "User not found."}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token!'}), 401
    except Exception as e:
        return jsonify({'error': f'Profile fetch error: {str(e)}'}), 500
    

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM admins WHERE email = :email"),
                {"email": email}
            )
            admin = result.fetchone()

        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        stored_password = admin[3] 
        if not check_password_hash(stored_password, password):
            return jsonify({"error": "Invalid password"}), 401

        token_payload = {
            "email": email,
            "role": "admin",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        }

        admin_token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        response = make_response(jsonify({"message": "Admin login successful!"}))
        response.set_cookie(
            "admin_token", admin_token,
            httponly=True,
            samesite="Lax",
            max_age=6 * 60 * 60  # 6 hours
        )

        return response

    except Exception as e:
        print(f"[ERROR] Admin login failed: {str(e)}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500




@app.route("/api/admin/users", methods=["GET"])
@admin_required
def list_users():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT username, email, request_count, active FROM users")
            )
            users = [
                {
                    "username": row[0],
                    "email": row[1],
                    "request_count": row[2],
                    "active": row[3]
                }
                for row in result.fetchall()
            ]

        return jsonify({"users": users}), 200

    except Exception as e:
        print(f"[ERROR] Admin user fetch failed: {str(e)}")
        return jsonify({"error": "Failed to fetch users"}), 500
    



@app.route("/api/admin/ban_user", methods=["POST"])
@admin_required
def ban_user():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required"}), 400
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET active = FALSE WHERE email = :email"),
                {"email": email}
            )
        return jsonify({"message": f"User '{email}' has been temprorarily banned."}), 200
        

    except Exception as e:
        print(f"[ERROR] Failed to ban user: {str(e)}")
        return jsonify({"error": "Failed to ban user"}), 500

@app.route("/api/admin/unban_user", methods=["POST"])
@admin_required
def unban_user():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required"}), 400
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET active = TRUE WHERE email = :email"),
                {"email": email}
            )
        return jsonify({"message": f"User '{email}' has been restored."}), 200

    except Exception as e:
        print(f"[ERROR] Failed to unban user: {str(e)}")
        return jsonify({"error": "Failed to unban user"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8510, debug=False)