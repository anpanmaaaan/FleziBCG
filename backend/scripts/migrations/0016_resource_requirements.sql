-- Migration: 0016_resource_requirements.sql
-- Introduces: resource_requirements table for P0-B-03 Resource Requirement Mapping.
-- Dependencies: routings and routing_operations tables (0015_routings.sql) must exist.

CREATE TABLE IF NOT EXISTS resource_requirements (
    requirement_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    routing_id VARCHAR(64) NOT NULL REFERENCES routings(routing_id),
    operation_id VARCHAR(64) NOT NULL REFERENCES routing_operations(operation_id),
    required_resource_type VARCHAR(64) NOT NULL,
    required_capability_code VARCHAR(128) NOT NULL,
    quantity_required INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    metadata_json TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_rr_tenant_operation_type_capability
        UNIQUE (tenant_id, operation_id, required_resource_type, required_capability_code)
);

CREATE INDEX IF NOT EXISTS ix_resource_requirements_tenant_id ON resource_requirements(tenant_id);
CREATE INDEX IF NOT EXISTS ix_resource_requirements_routing_id ON resource_requirements(routing_id);
CREATE INDEX IF NOT EXISTS ix_resource_requirements_operation_id ON resource_requirements(operation_id);
