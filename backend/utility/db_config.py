# db_config.py
import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv
import psycopg2 


load_dotenv()


db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')

encoded_password = urllib.parse.quote_plus(db_password)

connection_string = f"postgresql://{db_username}:{encoded_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

def get_db_connection():
    return psycopg2.connect(
        dbname=db_name,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port
    )