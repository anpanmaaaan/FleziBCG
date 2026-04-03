-- Phase 6C Step 2: Impersonation sessions and audit trail

CREATE TABLE IF NOT EXISTS impersonation_sessions (
    id SERIAL PRIMARY KEY,
    real_user_id VARCHAR(64) NOT NULL,
    real_role_code VARCHAR(32) NOT NULL,
    acting_role_code VARCHAR(32) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    reason VARCHAR(512) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS impersonation_audit_logs (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES impersonation_sessions(id) ON DELETE CASCADE,
    real_user_id VARCHAR(64) NOT NULL,
    acting_role_code VARCHAR(32) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    permission_family VARCHAR(64),
    endpoint VARCHAR(256),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_impersonation_sessions_real_user_tenant
    ON impersonation_sessions(real_user_id, tenant_id);
CREATE INDEX IF NOT EXISTS ix_impersonation_sessions_active
    ON impersonation_sessions(real_user_id, tenant_id, expires_at)
    WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS ix_impersonation_audit_logs_session
    ON impersonation_audit_logs(session_id);
