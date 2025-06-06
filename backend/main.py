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
from utility.db_config import engine 
from chat_rag import chat_blueprint 

from utility.scraper_and_embedder import scrape_wakawell_pages
from utility.embedder import prepare_documents, embed_and_store_documents
import datetime
import json

active_logins = {}  

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

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

#for forgot password functionality
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')
        security_question = data.get('security_question')
        security_answer = data.get('security_answer')

        # Validate required fields
        if not name or not email or not password or not security_question or not security_answer:
            return jsonify({"error": "All fields are required."}), 400

        hashed_password = generate_password_hash(password)
        hashed_questions = {
            security_question: generate_password_hash(security_answer.strip().lower())
        }

        with engine.begin() as connection:
            # Check if user already exists
            result = connection.execute(
                text("SELECT email FROM users WHERE email = :email"),
                {'email': email}
            )
            if result.fetchone():
                return jsonify({"error": "User with this email already exists. Please log in."}), 400

            # Insert user without id
            connection.execute(
                text("""
                    INSERT INTO users (username, email, password, security_questions)
                    VALUES (:username, :email, :password, :security_questions)
                """),
                {
                    'username': name,
                    'email': email,
                    'password': hashed_password,
                    'security_questions': json.dumps(hashed_questions)
                }
            )

        return jsonify({"message": "Signup successful! Please log in."}), 201

    except Exception as e:
        print(f"[SIGNUP ERROR] {e}")
        return jsonify({"error": "Signup failed. Please try again later."}), 500

@app.route('/api/get-security-question', methods=['POST'])
def get_security_question():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required."}), 400

        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT security_questions FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()

        if not user:
            return jsonify({"error": "User not found."}), 404

        stored_questions_json = user[0]
        if not stored_questions_json:
            return jsonify({"error": "Security question not set."}), 400

        # Handle possible JSON format
        if isinstance(stored_questions_json, str):
            stored_questions = json.loads(stored_questions_json)
        elif isinstance(stored_questions_json, dict):
            stored_questions = stored_questions_json
        else:
            return jsonify({"error": "Invalid format of stored security questions."}), 500

        if len(stored_questions) != 1:
            return jsonify({"error": "Invalid number of stored security questions."}), 500

        question = list(stored_questions.keys())[0]
        return jsonify({"question": question}), 200

    except Exception as e:
        print(f"[GET SECURITY QUESTION ERROR] {e}")
        return jsonify({"error": "Something went wrong. Please try again later."}), 500

@app.route('/api/verify-security-answer', methods=['POST'])
def verify_security_answer():
    try:
        data = request.get_json()
        email = data.get("email")
        security_question = data.get("security_question")
        security_answer = data.get("security_answer")

        if not email or not security_question or not security_answer:
            return jsonify({"error": "All fields are required."}), 400

        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT security_questions FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()

        if not user:
            return jsonify({"error": "User not found."}), 404

        stored_questions_json = user[0]
        if isinstance(stored_questions_json, str):
            stored_questions = json.loads(stored_questions_json)
        elif isinstance(stored_questions_json, dict):
            stored_questions = stored_questions_json
        else:
            return jsonify({"error": "Invalid format of stored security questions."}), 500

        hashed_answer = stored_questions.get(security_question)
        if not hashed_answer:
            return jsonify({"error": "Security question mismatch."}), 403

        if not check_password_hash(hashed_answer, security_answer.strip().lower()):
            return jsonify({"error": "Incorrect security answer."}), 403

        return jsonify({"message": "Security answer verified successfully."}), 200

    except Exception as e:
        print(f"[VERIFY SECURITY ANSWER ERROR] {e}")
        return jsonify({"error": "Failed to verify security answer. Please try again later."}), 500

@app.route('/api/update-password', methods=['POST'])
def update_password():
    try:
        data = request.get_json()
        email = data.get("email")
        security_question = data.get("security_question")
        security_answer = data.get("security_answer")
        new_password = data.get("new_password")

        if not email or not security_question or not security_answer or not new_password:
            return jsonify({"error": "All fields are required."}), 400

        with engine.begin() as connection:
            result = connection.execute(
                text("SELECT security_questions FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()

            if not user:
                return jsonify({"error": "User not found."}), 404

            stored_questions_json = user[0]
            if isinstance(stored_questions_json, str):
                stored_questions = json.loads(stored_questions_json)
            elif isinstance(stored_questions_json, dict):
                stored_questions = stored_questions_json
            else:
                return jsonify({"error": "Invalid format of stored security questions."}), 500

            hashed_answer = stored_questions.get(security_question)
            if not hashed_answer:
                return jsonify({"error": "Security question mismatch."}), 403

            if not check_password_hash(hashed_answer, security_answer.strip().lower()):
                return jsonify({"error": "Incorrect security answer."}), 403

            # All good — update password
            hashed_password = generate_password_hash(new_password)
            connection.execute(
                text("UPDATE users SET password = :password WHERE email = :email"),
                {"password": hashed_password, "email": email}
            )

        return jsonify({"message": "Password updated successfully. Please log in."}), 200

    except Exception as e:
        print(f"[UPDATE PASSWORD ERROR] {e}")
        return jsonify({"error": "Failed to update password. Please try again later."}), 500


@app.route('/api/login', methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        with engine.begin() as connection:
            # Check session_active status
            session_result = connection.execute(
                text("SELECT session_active FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()

            if session_result and session_result[0]:  # session_active == TRUE
                #  Check if existing token is still valid
                token = request.cookies.get("auth_token")
                token_expired = False
        
                if token:
                    try:
                        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                        # Token still valid → deny login
                        return jsonify({"error": "User already logged in from another session!"}), 403
                    except jwt.ExpiredSignatureError:
                        token_expired = True
                    except jwt.InvalidTokenError:
                        token_expired = True
                else:
                    token_expired = True

                # Token expired or missing → reset session_active
                if token_expired:
                    connection.execute(
                        text("UPDATE users SET session_active = FALSE WHERE email = :email"),
                        {"email": email}
                    )

            # Fetch full user data
            result = connection.execute(
                text("SELECT username, email, password, active FROM users WHERE email = :email"),
                {'email': email}
            )
            user = result.fetchone()
            print("user",user)

            if not user:
                return jsonify({"error": "User does not exist!"}), 404

            if not check_password_hash(user[2], password):
                return jsonify({"error": "Invalid password!"}), 401

            if not user[3]:  # 'active' column
                return jsonify({"error": "User is temporarily banned. Please contact admin."}), 403

            # Mark session as active
            connection.execute(
                text("UPDATE users SET session_active = TRUE WHERE email = :email"),
                {"email": email}
            )

        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        # Set the token as a cookie
        response = make_response(jsonify({"message": "Login successful!", "token": token}))
        response.set_cookie(
            "auth_token", token,
            httponly=True,
            samesite="Lax",
            max_age=1800
        )
        return response

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@app.route('/api/logout', methods=["POST"])
@token_required
def logout(email):  
    session_contexts.pop(email, None)

    # active_logins.pop(email, None)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE users SET session_active = FALSE WHERE email = :email"),
            {"email": email}
        )

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
            
            result = connection.execute(
                text("SELECT username, email, source_country, destination_country FROM users WHERE email = :email"),
                {'email': email}
            )
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
                "source_country": user[2],
                "destination_country": user[3],
                "message": "User profile fetched successfully.",
                "conversation": formatted_messages
            }), 200
        else:
            return jsonify({"error": "User not found."}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Session expired. Please log in again.'}), 401
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

@app.route("/api/admin/profile", methods=["GET"])
@admin_required
def admin_profile():
    try:
        token = request.cookies.get("admin_token")
        if not token:
            return jsonify({"error": "Missing token"}), 401

        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        email = data.get("email")

        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT username, email FROM admins WHERE email = :email"),
                {"email": email}
            )
            admin = result.fetchone()

        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        return jsonify({
            "username": admin[0],
            "email": admin[1],
            "message": "Admin profile fetched successfully."
        }), 200

    except Exception as e:
        print(f"[ERROR] Admin profile fetch failed: {str(e)}")
        return jsonify({"error": "Failed to fetch admin profile"}), 500


@app.route("/api/admin/add-url", methods=["POST"])
@admin_required
def add_url():
    try:
        data = request.get_json()
        email = data.get("email")  # email from body
        new_url = data.get("url")

        if not email or not new_url or not new_url.startswith(("http://", "https://")):
            return jsonify({"error": "Invalid or missing URL/email"}), 400

        # Verify the email matches token
        token = request.cookies.get("admin_token")
        decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        token_email = decoded.get("email")

        if token_email != email:
            return jsonify({"error": "Email mismatch with authenticated admin"}), 403

        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "urls.json"))

        # Load existing URLs
        with open(config_path, "r", encoding="utf-8") as f:
            urls = json.load(f)

        # if new_url in urls:
        #     return jsonify({"message": "URL already exists in the list"}), 200
        if new_url in urls:
            return jsonify({
                "status": "duplicate",
                "message": "URL already exists in the list",
                "url": new_url
            }), 409 


        urls.append(new_url)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(urls, f, indent=2)

        #  (Optional) log entry for future tracking
        print(f"[AUDIT] Admin '{email}' added URL: {new_url}")

        # return jsonify({"message": "URL added successfully", "urls": urls}), 200
        return jsonify({
            "message": "URL added successfully",
            "added_url": new_url
        }), 200


    except Exception as e:
        print(f"[ERROR] Failed to add URL: {str(e)}")
        return jsonify({"error": "Failed to add URL"}), 500


@app.route("/api/admin/urls", methods=["GET"])
@admin_required
def list_all_urls():
    try:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "urls.json"))
        with open(config_path, "r", encoding="utf-8") as f:
            urls = json.load(f)

        return jsonify({
            "urls": urls,
            "count": len(urls),
            "message": "URL list fetched successfully"
        }), 200

    except Exception as e:
        print(f"[ERROR] Failed to load URL list: {str(e)}")
        return jsonify({"error": "Could not retrieve URL list"}), 500


@app.route("/api/admin/extract", methods=["POST"])
@admin_required
def run_extraction():
    try:
        # Step 1: Scrape
        print("Starting website scrape...")
        scraped_data = scrape_wakawell_pages()

        if not scraped_data:
            return jsonify({"status": "failure", "message": "No content scraped."}), 400

        # Step 2: Save to timestamped file
        timestamp = datetime.datetime.now()
        timestamp_str = timestamp.strftime("%Y_%m_%d_%H_%M")
        versioned_file = f"scraped_data_{timestamp_str}.json"
        latest_file = "scraped_data_full.json"

        with open(versioned_file, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)

        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        
        with open("metadata.json", "w") as f:
            json.dump({"last_updated_on": timestamp.strftime("%Y-%m-%d %H:%M:%S")}, f)

        print(f" Scraped data saved to {versioned_file} and updated {latest_file}")

        # Step 3: Embed and save to Chroma
        print(" Preparing and embedding content...")
        documents = prepare_documents(scraped_data)
        embed_and_store_documents(documents)

        # Step 4: Update admin last_update_on
        admin_token = request.cookies.get("admin_token")
        decoded = jwt.decode(admin_token, app.config["SECRET_KEY"], algorithms=["HS256"])
        admin_email = decoded.get("email")

        # with engine.begin() as connection:
        #     connection.execute(
        #         text("UPDATE admins SET last_update_on = :ts WHERE email = :email"),
        #         {"ts": timestamp, "email": admin_email}
        #     )

        # Step 5: Build frontend-friendly response
        extracted_sections = [
            {"title": item["title"], "text": item["text"]}
            for item in scraped_data if item.get("title") and item.get("text")
        ]

        return jsonify({
            "status": "success",
            "message": "Scraping and embedding completed.",
            "last_updated_on": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "sections": extracted_sections
        }), 200

    except Exception as e:
        print(f"[ERROR] Extraction failed: {str(e)}")
        return jsonify({"status": "failure", "message": "Extraction failed."}), 500

@app.route("/api/admin/extractions", methods=["GET"])
@admin_required
def get_latest_extracted_data():
    try:
        import json

        with open("scraped_data_full.json", "r", encoding="utf-8") as f:
            sections = json.load(f)

        with open("metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

        return jsonify({
            "status": "success",
            "last_updated_on": meta.get("last_updated_on"),
            "sections": sections
        }), 200

    except FileNotFoundError:
        return jsonify({
            "status": "empty",
            "message": "No extracted data found."
        }), 404

    except Exception as e:
        print(f"[ERROR] Failed to load extracted data: {str(e)}")
        return jsonify({
            "status": "failure",
            "message": "Something went wrong loading extracted content."
        }), 500


@app.route("/api/admin/upload-doc", methods=["POST"])
@admin_required
def upload_doc():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        uploaded_file = request.files["file"]
        email = request.form.get("email")

        if not uploaded_file or uploaded_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not email:
            return jsonify({"error": "Missing admin email"}), 400

        filename = uploaded_file.filename
        save_dir = "docs"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join("docs", filename)

        uploaded_file.save(save_path)
        print(f" File saved to: {save_path}")

        # Embed using your embedder logic
        from utility.embedder import embed_uploaded_file
        result = embed_uploaded_file(save_path, uploaded_by=email)

        return jsonify(result), 200 if result["status"] == "success" else 409

    except Exception as e:
        print(f" Upload error: {e}")
        return jsonify({"error": "Upload failed", "message": str(e)}), 500


@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    response = make_response(jsonify({"message": "Admin logged out successfully!"}))
    response.set_cookie("admin_token", "", expires=0)
    return response

@app.route("/api/db-health", methods=["GET"])
def db_health():
    try:
        # This just does a minimal query; if it fails, we catch it below
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[DB HEALTH-ERROR] {e}")
        return jsonify({"status": "fail", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)