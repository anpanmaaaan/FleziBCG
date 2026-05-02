-- Migration: 0018_product_versions.sql
-- Introduces: product_versions table for P0-B MMD baseline (MMD-BE-03).
-- Dependencies: products table (0014_products.sql) must exist.
--
-- WHY: Product Version is the minimal read model for versioned manufacturing
-- definition context. No BOM/Routing/RR bindings in this revision.

CREATE TABLE IF NOT EXISTS product_versions (
    product_version_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id),
    version_code VARCHAR(64) NOT NULL,
    version_name VARCHAR(256),
    lifecycle_status VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    effective_from DATE,
    effective_to DATE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_product_versions_tenant_product_code
        UNIQUE (tenant_id, product_id, version_code)
);

CREATE INDEX IF NOT EXISTS ix_product_versions_tenant_id ON product_versions(tenant_id);
CREATE INDEX IF NOT EXISTS ix_product_versions_product_id ON product_versions(product_id);
CREATE INDEX IF NOT EXISTS ix_product_versions_tenant_product ON product_versions(tenant_id, product_id);
