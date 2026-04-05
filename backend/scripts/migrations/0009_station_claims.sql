-- Station Execution v2: station queue + mandatory operation claims

ALTER TABLE operations
    ADD COLUMN IF NOT EXISTS station_scope_value VARCHAR(128) NOT NULL DEFAULT 'STATION_01';

CREATE INDEX IF NOT EXISTS ix_operations_station_scope_value
    ON operations (station_scope_value);

UPDATE operations
SET station_scope_value = COALESCE(NULLIF(station_scope_value, ''), 'STATION_01')
WHERE station_scope_value IS NULL OR station_scope_value = '';

CREATE TABLE IF NOT EXISTS operation_claims (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    operation_id INTEGER NOT NULL REFERENCES operations(id),
    station_scope_id INTEGER NOT NULL REFERENCES scopes(id),
    claimed_by_user_id VARCHAR(64) NOT NULL,
    claimed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    released_at TIMESTAMPTZ NULL,
    release_reason VARCHAR(256) NULL
);

CREATE INDEX IF NOT EXISTS ix_operation_claims_tenant_id ON operation_claims(tenant_id);
CREATE INDEX IF NOT EXISTS ix_operation_claims_operation_id ON operation_claims(operation_id);
CREATE INDEX IF NOT EXISTS ix_operation_claims_station_scope_id ON operation_claims(station_scope_id);
CREATE INDEX IF NOT EXISTS ix_operation_claims_claimed_by_user_id ON operation_claims(claimed_by_user_id);
CREATE INDEX IF NOT EXISTS ix_operation_claims_expires_at ON operation_claims(expires_at);

-- Keep a single unresolved claim row per operation. Expired rows are auto-released in service logic.
CREATE UNIQUE INDEX IF NOT EXISTS uq_operation_claims_operation_active
    ON operation_claims(operation_id)
    WHERE released_at IS NULL;

CREATE TABLE IF NOT EXISTS operation_claim_audit_logs (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER NULL REFERENCES operation_claims(id),
    tenant_id VARCHAR(64) NOT NULL,
    operation_id INTEGER NOT NULL REFERENCES operations(id),
    station_scope_id INTEGER NOT NULL REFERENCES scopes(id),
    actor_user_id VARCHAR(64) NOT NULL,
    acting_role_code VARCHAR(32) NULL,
    event_type VARCHAR(64) NOT NULL,
    reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_operation_claim_audit_logs_claim_id ON operation_claim_audit_logs(claim_id);
CREATE INDEX IF NOT EXISTS ix_operation_claim_audit_logs_tenant_id ON operation_claim_audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS ix_operation_claim_audit_logs_operation_id ON operation_claim_audit_logs(operation_id);
CREATE INDEX IF NOT EXISTS ix_operation_claim_audit_logs_station_scope_id ON operation_claim_audit_logs(station_scope_id);
