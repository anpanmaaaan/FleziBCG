-- Migration: 0020_reason_codes.sql
-- Introduces: reason_codes table for unified reason code foundation (MMD-BE-07).
-- Alembic mirror: 0010_reason_codes.py (Revision ID: 0010, down_revision: 0009)
--
-- WHY: Per reason-code-foundation-contract.md v1.0 (Sections 6-8), implement
-- minimal unified reason code reference data model. Reason codes provide
-- classification context across operational domains (execution, downtime,
-- quality, material, maintenance) without owning operational events.
--
-- Boundary lock:
-- - Read-only reference data table. No write endpoints in this revision.
-- - Tenant-scoped only (no plant/area/line/station hierarchy in this revision).
-- - Independent of downtime_reasons table. No FK references between them.
-- - No FK to execution, quality, or material tables.
-- - lifecycle_status values: DRAFT | RELEASED | RETIRED (MMD standard).
-- - Write path (POST/PATCH) and lifecycle transitions deferred to MMD-BE-08+.
-- - downtime_reasons table remains untouched.

CREATE TABLE IF NOT EXISTS reason_codes (
    reason_code_id VARCHAR(64) PRIMARY KEY,
    tenant_id      VARCHAR(64) NOT NULL,
    reason_domain  VARCHAR(32) NOT NULL,
    reason_category VARCHAR(64) NOT NULL,
    reason_code    VARCHAR(64) NOT NULL,
    reason_name    VARCHAR(128) NOT NULL,
    description    TEXT,
    lifecycle_status VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
    requires_comment BOOLEAN    NOT NULL DEFAULT FALSE,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    sort_order     INTEGER      NOT NULL DEFAULT 0,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_reason_codes_tenant_domain_code
        UNIQUE (tenant_id, reason_domain, reason_code)
);

CREATE INDEX IF NOT EXISTS ix_reason_codes_tenant_id
    ON reason_codes (tenant_id);

CREATE INDEX IF NOT EXISTS ix_reason_codes_tenant_domain_category
    ON reason_codes (tenant_id, reason_domain, reason_category);

CREATE INDEX IF NOT EXISTS ix_reason_codes_tenant_status_active
    ON reason_codes (tenant_id, lifecycle_status, is_active);
