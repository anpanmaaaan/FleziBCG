CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    product_code VARCHAR(64) NOT NULL,
    product_name VARCHAR(256) NOT NULL,
    product_type VARCHAR(32) NOT NULL,
    lifecycle_status VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
    description TEXT,
    display_metadata TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_products_tenant_code UNIQUE (tenant_id, product_code)
);

CREATE INDEX IF NOT EXISTS ix_products_tenant_id ON products(tenant_id);
CREATE INDEX IF NOT EXISTS ix_products_tenant_code ON products(tenant_id, product_code);
