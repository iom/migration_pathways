import os
import jwt
from functools import wraps
from flask import request, jsonify
from sqlalchemy import create_engine, text
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# Load secret key and JWT algorithm
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# DB config (for user validation)
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

encoded_password = urllib.parse.quote_plus(db_password)
connection_string = f"postgresql://{db_username}:{encoded_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("auth_token")  #  Only from cookie

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("email")

            if not email:
                return jsonify({"error": "Invalid token payload"}), 401

            # Optional: validate user exists in DB
            with engine.connect() as connection:
                result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {'email': email})
                user = result.fetchone()

            if not user:
                return jsonify({'error': 'User does not exist!'}), 401

            return f(email, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication error: {str(e)}"}), 500

    return decorated
