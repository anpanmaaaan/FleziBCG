CREATE TABLE IF NOT EXISTS security_event_logs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    actor_user_id VARCHAR(64),
    event_type VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64),
    resource_id VARCHAR(128),
    detail TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_security_event_logs_tenant ON security_event_logs(tenant_id);
CREATE INDEX IF NOT EXISTS ix_security_event_logs_actor ON security_event_logs(actor_user_id);
CREATE INDEX IF NOT EXISTS ix_security_event_logs_event_type ON security_event_logs(event_type);
CREATE INDEX IF NOT EXISTS ix_security_event_logs_created_at ON security_event_logs(created_at);
