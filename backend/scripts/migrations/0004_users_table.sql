-- Step 6D-1: Users table for authentication

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL UNIQUE,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(256),
    password_hash VARCHAR(256) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_username_tenant UNIQUE (username, tenant_id)
);

CREATE INDEX IF NOT EXISTS ix_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS ix_users_username_tenant ON users(username, tenant_id);
CREATE INDEX IF NOT EXISTS ix_users_tenant ON users(tenant_id);
