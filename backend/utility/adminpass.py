import psycopg2
from werkzeug.security import generate_password_hash

# Flask App Secret Key
SECRET_KEY="hjsd78hdhd$$sjsjs###23y2h"

# Database Configuration
DB_USERNAME="iom_uc2_user"
DB_PASSWORD="IomUC2@20250321$"
DB_HOST="ec2-43-205-148-102.ap-south-1.compute.amazonaws.com"
DB_PORT="5432"
DB_NAME="iom_uc2"

 
admin_passwords = {
    "admin1@example.com": "adminpass1",
    "admin2@example.com": "adminpass2",
    "admin3@example.com": "adminpass3",
    "admin4@example.com": "adminpass4",
    "admin5@example.com": "adminpass5"
}

def update_passwords():
    try:
       
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

       
        for email, plain_password in admin_passwords.items():
            hashed_password = generate_password_hash(plain_password)
            cursor.execute(
                "UPDATE admins SET password = %s WHERE email = %s",
                (hashed_password, email)
            )
            print(f"Updated password for {email}")

        cursor.close()
        conn.close()
        print("\nAll admin passwords updated successfully.")

    except Exception as e:
        print(f"error updating passwords: {e}")

if __name__ == "__main__":
    update_passwords()