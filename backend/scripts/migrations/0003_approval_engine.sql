-- Phase 6C Step 3: Approval Engine

CREATE TABLE IF NOT EXISTS approval_rules (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(64) NOT NULL,
    approver_role_code VARCHAR(32) NOT NULL,
    tenant_id VARCHAR(64) NOT NULL DEFAULT '*',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_approval_rule UNIQUE (action_type, approver_role_code, tenant_id)
);

CREATE TABLE IF NOT EXISTS approval_requests (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    requester_id VARCHAR(64) NOT NULL,
    requester_role_code VARCHAR(32),
    subject_type VARCHAR(64),
    subject_ref VARCHAR(256),
    reason VARCHAR(512) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approval_decisions (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES approval_requests(id) ON DELETE CASCADE,
    decider_id VARCHAR(64) NOT NULL,
    decider_role_code VARCHAR(32),
    decision VARCHAR(32) NOT NULL,
    comment VARCHAR(512),
    impersonation_session_id INTEGER REFERENCES impersonation_sessions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approval_audit_logs (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES approval_requests(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL,
    role_code VARCHAR(32),
    tenant_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    detail VARCHAR(512),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_approval_rules_action_type
    ON approval_rules(action_type);

CREATE INDEX IF NOT EXISTS ix_approval_requests_tenant
    ON approval_requests(tenant_id);

CREATE INDEX IF NOT EXISTS ix_approval_requests_action_type
    ON approval_requests(action_type);

CREATE INDEX IF NOT EXISTS ix_approval_requests_status
    ON approval_requests(status);

CREATE INDEX IF NOT EXISTS ix_approval_requests_pending
    ON approval_requests(tenant_id, status)
    WHERE status = 'PENDING';

CREATE INDEX IF NOT EXISTS ix_approval_decisions_request
    ON approval_decisions(request_id);

CREATE INDEX IF NOT EXISTS ix_approval_audit_logs_request
    ON approval_audit_logs(request_id);

-- Seed default approval rules
INSERT INTO approval_rules (action_type, approver_role_code, tenant_id) VALUES
    ('QC_HOLD',    'QAL', '*'),
    ('QC_RELEASE', 'QAL', '*'),
    ('SCRAP',      'QAL', '*'),
    ('SCRAP',      'PMG', '*'),
    ('REWORK',     'QAL', '*'),
    ('WO_SPLIT',   'PMG', '*'),
    ('WO_MERGE',   'PMG', '*')
ON CONFLICT (action_type, approver_role_code, tenant_id) DO NOTHING;
