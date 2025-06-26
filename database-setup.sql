-- Database setup for Migration Pathways App
-- IMPORTANT ****** CHANGE <DB_USER> TO DB_USERNAME ********

-- Grant necessary privileges to the application user
GRANT CONNECT ON DATABASE postgres TO <DB_USER>;
GRANT USAGE ON SCHEMA public TO <DB_USER>;

-- Create Users table
CREATE TABLE IF NOT EXISTS public.users (
	username varchar(50) NOT NULL,
	email varchar(100) NOT NULL,
	"password" varchar(255) NOT NULL,
	request_count int4 DEFAULT 0 NULL,
	active bool DEFAULT true NULL,
	source_country varchar(100) NULL,
	destination_country varchar(100) NULL,
	session_active bool DEFAULT false NULL,
	security_questions jsonb NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (username)    
);


-- Create Admins table
CREATE TABLE IF NOT EXISTS public.admins (
	id serial4 NOT NULL,
	username text NOT NULL,
	email text NOT NULL,
	"password" text NOT NULL,  -- we'll store hashed passwords here
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT admins_email_key UNIQUE (email),
	CONSTRAINT admins_pkey PRIMARY KEY (id)
);

-- Create embeddings table for PGVECTOR
CREATE TABLE IF NOT EXISTS public.embeddings (
	id uuid NOT NULL,
	"content" text NOT NULL,
	embedding public.vector NULL,
	"source" text NULL,
	source_url text NULL,
	title text NULL,
	file_hash text NULL,
	filename text NULL,
	uploaded_by text NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,       
	CONSTRAINT embeddings_pkey PRIMARY KEY (id)
);

-- Create conversation_history table
CREATE TABLE IF NOT EXISTS public.conversation_history (
	id uuid NOT NULL,
	email text NULL,
	user_message text NOT NULL,
	bot_response text NOT NULL,
	"timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	session_id text NULL,
	sources jsonb NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,    
	CONSTRAINT conversation_history_pkey PRIMARY KEY (id)
);

-- public.conversation_history foreign keys
ALTER TABLE public.conversation_history ADD CONSTRAINT conversation_history_email_fkey FOREIGN KEY (email) REFERENCES public.users(email) ON DELETE CASCADE;


-- Create index for faster user lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Grant table permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO <DB_USER>;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO <DB_USER>;
