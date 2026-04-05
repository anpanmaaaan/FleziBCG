-- Tier 1 v2 Step A: hierarchical scopes and role assignments

CREATE TABLE IF NOT EXISTS scopes (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    scope_type VARCHAR(32) NOT NULL,
    scope_value VARCHAR(128) NOT NULL,
    parent_scope_id INTEGER REFERENCES scopes(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_scope_tenant_type_value UNIQUE (tenant_id, scope_type, scope_value)
);

CREATE INDEX IF NOT EXISTS ix_scopes_tenant ON scopes(tenant_id);
CREATE INDEX IF NOT EXISTS ix_scopes_type ON scopes(scope_type);
CREATE INDEX IF NOT EXISTS ix_scopes_value ON scopes(scope_value);
CREATE INDEX IF NOT EXISTS ix_scopes_parent ON scopes(parent_scope_id);

CREATE TABLE IF NOT EXISTS user_role_assignments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    scope_id INTEGER NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_role_assignment_scope UNIQUE (user_id, role_id, scope_id)
);

CREATE INDEX IF NOT EXISTS ix_user_role_assignments_user ON user_role_assignments(user_id);
CREATE INDEX IF NOT EXISTS ix_user_role_assignments_role ON user_role_assignments(role_id);
CREATE INDEX IF NOT EXISTS ix_user_role_assignments_scope ON user_role_assignments(scope_id);
CREATE INDEX IF NOT EXISTS ix_user_role_assignments_active ON user_role_assignments(is_active);
