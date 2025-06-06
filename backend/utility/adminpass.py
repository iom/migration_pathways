# utility/reset_admin_pass.py

from werkzeug.security import generate_password_hash
import getpass
from db_config import get_db_connection

def reset_password(email, new_password):
    try:
        conn = get_db_connection()
        conn.autocommit = True
        cursor = conn.cursor()

        # Use Werkzeug's generate_password_hash (which uses scrypt by default)
        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE admins SET password = %s WHERE email = %s",
            (hashed_password, email)
        )

        print(f" Password successfully reset for {email}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f" Error resetting password: {e}")

if __name__ == "__main__":
    email = input("Enter admin email: ").strip()
    new_password = getpass.getpass("Enter new password: ").strip()

    if email and new_password:
        reset_password(email, new_password)
    else:
        print(" Email or password cannot be empty.")
