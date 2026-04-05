-- Tier 1 v2 Step D: custom-role governance and action-code permissions

ALTER TABLE roles ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(64);
ALTER TABLE roles ADD COLUMN IF NOT EXISTS role_type VARCHAR(16) NOT NULL DEFAULT 'system';
ALTER TABLE roles ADD COLUMN IF NOT EXISTS base_role_id INTEGER REFERENCES roles(id);
ALTER TABLE roles ADD COLUMN IF NOT EXISTS owner_user_id VARCHAR(64);
ALTER TABLE roles ADD COLUMN IF NOT EXISTS review_due_at TIMESTAMPTZ;
ALTER TABLE roles ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

CREATE INDEX IF NOT EXISTS ix_roles_tenant_id ON roles(tenant_id);

ALTER TABLE permissions ADD COLUMN IF NOT EXISTS action_code VARCHAR(128);
CREATE INDEX IF NOT EXISTS ix_permissions_action_code ON permissions(action_code);

ALTER TABLE role_permissions ADD COLUMN IF NOT EXISTS effect VARCHAR(8) NOT NULL DEFAULT 'allow';
