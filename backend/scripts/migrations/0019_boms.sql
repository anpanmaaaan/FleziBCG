-- Migration: 0019_boms.sql
-- Introduces: boms and bom_items tables for MMD-BE-05.
-- Dependencies: products table (0014_products.sql) must exist.
--
-- Boundary lock:
-- - Product-scoped BOM read model only.
-- - No product_version_id in this revision.
-- - No material movement, backflush, ERP posting, genealogy, or quality
--   runtime behavior fields.

CREATE TABLE IF NOT EXISTS boms (
    bom_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id),
    bom_code VARCHAR(64) NOT NULL,
    bom_name VARCHAR(256) NOT NULL,
    lifecycle_status VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
    effective_from DATE,
    effective_to DATE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_boms_tenant_product_code
        UNIQUE (tenant_id, product_id, bom_code)
);

CREATE INDEX IF NOT EXISTS ix_boms_tenant_id ON boms(tenant_id);
CREATE INDEX IF NOT EXISTS ix_boms_product_id ON boms(product_id);
CREATE INDEX IF NOT EXISTS ix_boms_tenant_product ON boms(tenant_id, product_id);

CREATE TABLE IF NOT EXISTS bom_items (
    bom_item_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    bom_id VARCHAR(64) NOT NULL REFERENCES boms(bom_id),
    component_product_id VARCHAR(64) NOT NULL REFERENCES products(product_id),
    line_no INTEGER NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    unit_of_measure VARCHAR(32) NOT NULL,
    scrap_factor DOUBLE PRECISION,
    reference_designator VARCHAR(128),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_bom_items_tenant_bom_line_no
        UNIQUE (tenant_id, bom_id, line_no)
);

CREATE INDEX IF NOT EXISTS ix_bom_items_tenant_id ON bom_items(tenant_id);
CREATE INDEX IF NOT EXISTS ix_bom_items_bom_id ON bom_items(bom_id);
CREATE INDEX IF NOT EXISTS ix_bom_items_component_product_id ON bom_items(component_product_id);
CREATE INDEX IF NOT EXISTS ix_bom_items_tenant_bom ON bom_items(tenant_id, bom_id);
