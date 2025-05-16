#Migration Pathways – Immigration Assistant Chatbot

##Overview

This project contains the **backend code** for the **Migration Pathways** chatbot — an AI-powered assistant that helps users explore immigration options and pathways based on their personal circumstances.

The AI Assistant uses advanced search, language understanding, and data embedding techniques to assist users with their migration-related queries.

---

##Tech Stack

###Frontend
-ReactJS– for building an interactive user interface

###Backend
-Python – core logic and scripting
-Flask – lightweight backend server
-PostgreSQL– for persistent storage of users and admins

---

##PostgreSQL Setup

This backend requires a PostgreSQL database for storing user and admin data. Follow the steps below to install and configure PostgreSQL correctly.

### 1. Install PostgreSQL
Download and install PostgreSQL from the [official website](https://www.postgresql.org/download/), and ensure it's running locally or remotely.
- During setup, make note of:
  - **Username** (default: `postgres`)
  - **Password**
  - **Port** (default: `5432`)
- Once installed, launch **pgAdmin** or use the terminal to interact with PostgreSQL.

###  2. Create a Database and User

Open the PostgreSQL terminal (`psql`) or use pgAdmin:

```sql
-- Log in as the default PostgreSQL superuser
psql -U postgres

-- Create a new user for the project
CREATE USER iom_uc2_user WITH PASSWORD 'your_secure_password';

-- Create a new database
CREATE DATABASE iom_uc2;

-- Grant all privileges on the database to the new user
GRANT ALL PRIVILEGES ON DATABASE iom_uc2 TO iom_uc2_user;

\q  -- exit psql

### 3. Connect to the Database
psql -h localhost -U iom_uc2_user iom_uc2
After this Enter your password: 'your_secure_password'


### 4. Create Required Tables

Run the following SQL to set up the database schema:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    request_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL  -- we'll store hashed passwords here
);

### 3. Insert Sample Admin Records (Plaintext First)

Run the following SQL to create a sample admin account (before hashing):

```sql
INSERT INTO admins (username, email, password) VALUES
('IOM Admin', 'admin@iom-migration.in ', 'ChangeThisSecurely123');

### 4. Once the admins table created, to hash the password

#Run the python script:
python utilitly/adminpass.py 

### 5. Verify your setup
SELECT * FROM users;
SELECT * FROM admins;

Ensure that:
Admin passwords are hashed
Tables are correctly populated

### 6. First-time Setup and Run (Local Development)
# Step 1: Create a virtual environment
python -m venv iomuc2_env

# Step 2: Activate the virtual environment (Windows)
cd iomuc2_env/Scripts
activate

# Step 3: Move to the backend directory
cd ../../backend

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Run the embedding and scraping scripts (for preparing data)
python utility/scraper_and_embedder.py
python utility/embedder.py

# Step 6: Start the backend server
python main.py
