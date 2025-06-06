-- Database setup for Proposal Drafter application

-- Create application user (if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'iom_uc2_user') THEN
        CREATE USER iom_uc2_user WITH PASSWORD 'IomUC2@20250606$';
    END IF;
END $$;

-- Grant necessary privileges to the application user
GRANT CONNECT ON DATABASE postgres TO iom_uc2_user;
GRANT USAGE ON SCHEMA public TO iom_uc2_user;

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    username    VARCHAR(50) PRIMARY KEY,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    request_count INTEGER DEFAULT 0,
    active  BOOLEAN DEFAULT TRUE,
    source_country  VARCHAR(100),
    destination_country VARCHAR(100),
    session_active BOOLEAN DEFAULT FALSE,
    security_questions  JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create Admins table
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- we'll store hashed passwords here
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster user lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Grant table permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO iom_uc2_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO iom_uc2_user;

INSERT INTO admins (username, email, password) VALUES
('admin_one', 'admin1@migpathways.int', 'scrypt:32768:8:1$dle8xclSzfQapuxV$9bfb4550dd49a6cb55a041af05b18eabb64daef76cf219a9cdc1459e98622920a8b83e72e5fbaf19e0526b3c00f6305cf8cf9ac8b5a32e2fdcf7d1282326371f'),
('admin_three', 'admin3@migpathways.int', 'scrypt:32768:8:1$zxdqSFjCjJFGC1qv$faad8d1a9cc966c768ce45656b040e35a09a786591ead75f50d170cb94bef98322769ffb765b0993dd10702898e7de212b82e938c7eec7bdda9728e2a615bb30'),
('admin_four', 'admin4@migpathways.int', 'scrypt:32768:8:1$E2bRJEWh73vVtsn9$2371d41d6811776d1bdf64546e9580d22ec35f424c2d26c25398431adfeecfdf1fb33fce4b8642b0f3a4a2188e208c3de7ae1819625a8a43366bf76ffbb56a98'),
('admin_five', 'admin5@migpathways.int', 'scrypt:32768:8:1$uD5f52PVSZtiWy5T$9a65435738a1c2c094294094c2b5c69fcc7f65baca445c7922b50c55a568c5f799f96214da44bfc65e868aee323bd2fe928bb39a1a4049bd7d449ac48635f6fe'),
('admin_two', 'admin2@migpathways.int', 'scrypt:32768:8:1$FW4QTzwWBVUg5G2x$024a974fdc57e0ed67bfe69be938bf5893d7d7b944f478206adf37d258a34d4d08421b20ea65ca6dc2f55b9c758703b2767ea6dbbc0d1d08f4a6ec8d0534eaf3');

