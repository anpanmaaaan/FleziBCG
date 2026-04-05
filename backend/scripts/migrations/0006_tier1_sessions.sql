-- Tier 1 v2 Step C: session governance

CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    revoke_reason VARCHAR(256),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sessions_user_tenant ON sessions(user_id, tenant_id);
CREATE INDEX IF NOT EXISTS ix_sessions_tenant ON sessions(tenant_id);
CREATE INDEX IF NOT EXISTS ix_sessions_active ON sessions(user_id, tenant_id, expires_at) WHERE revoked_at IS NULL;

CREATE TABLE IF NOT EXISTS session_audit_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    tenant_id VARCHAR(64) NOT NULL,
    actor_user_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    detail VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_session_audit_logs_session ON session_audit_logs(session_id);
CREATE INDEX IF NOT EXISTS ix_session_audit_logs_tenant ON session_audit_logs(tenant_id);
