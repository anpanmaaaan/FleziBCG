-- Migration: 0015_routings.sql
-- Introduces: routings and routing_operations tables for P0-B-02 Routing Foundation.
-- Dependencies: products table (0014_products.sql) must exist before this migration.

CREATE TABLE IF NOT EXISTS routings (
    routing_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id),
    routing_code VARCHAR(64) NOT NULL,
    routing_name VARCHAR(256) NOT NULL,
    lifecycle_status VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_routings_tenant_code UNIQUE (tenant_id, routing_code)
);

CREATE INDEX IF NOT EXISTS ix_routings_tenant_id ON routings(tenant_id);
CREATE INDEX IF NOT EXISTS ix_routings_product_id ON routings(product_id);
CREATE INDEX IF NOT EXISTS ix_routings_tenant_code ON routings(tenant_id, routing_code);

CREATE TABLE IF NOT EXISTS routing_operations (
    operation_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    routing_id VARCHAR(64) NOT NULL REFERENCES routings(routing_id) ON DELETE CASCADE,
    operation_code VARCHAR(64) NOT NULL,
    operation_name VARCHAR(256) NOT NULL,
    sequence_no INTEGER NOT NULL,
    standard_cycle_time DOUBLE PRECISION,
    required_resource_type VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_routing_ops_sequence UNIQUE (routing_id, sequence_no)
);

CREATE INDEX IF NOT EXISTS ix_routing_operations_tenant_id ON routing_operations(tenant_id);
CREATE INDEX IF NOT EXISTS ix_routing_operations_routing_id ON routing_operations(routing_id);
