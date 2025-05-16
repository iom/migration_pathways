-- Create tables

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    request_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL  -- we'll store hashed passwords here
);

-- Insert initial admin user (with hashed password)
-- Note: In production, replace this with a proper hashed password
INSERT INTO admins (username, email, password) 
VALUES ('IOM Admin', 'admin@iom-migration.in', '$2b$12$YadHmIhlJ5Z5Lg6zzNjwGeSfz4y9oMcpDUpDkUj8ZCzD/LMPKNr4G') 
ON CONFLICT (email) DO NOTHING;