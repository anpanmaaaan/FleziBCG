-- Station Execution v3 enum refactor: move selectable downtime reasons from a
-- hardcoded classification enum into DB-backed master data. Platform-level
-- classification is expressed as reason_group values (see DowntimeReasonGroup
-- in app/models/downtime_reason.py) and persisted on each master row.
-- Scope columns (plant_code/area_code/line_code/station_scope_value) are
-- nullable today, baseline resolver uses tenant_id + reason_code only.

CREATE TABLE IF NOT EXISTS downtime_reasons (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    plant_code VARCHAR(64) NULL,
    area_code VARCHAR(64) NULL,
    line_code VARCHAR(64) NULL,
    station_scope_value VARCHAR(128) NULL,
    reason_code VARCHAR(64) NOT NULL,
    reason_name VARCHAR(128) NOT NULL,
    reason_group VARCHAR(32) NOT NULL,
    planned_flag BOOLEAN NOT NULL DEFAULT FALSE,
    default_block_mode VARCHAR(32) NOT NULL DEFAULT 'BLOCK',
    requires_comment BOOLEAN NOT NULL DEFAULT FALSE,
    requires_supervisor_review BOOLEAN NOT NULL DEFAULT FALSE,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_downtime_reasons_tenant_code
    ON downtime_reasons (tenant_id, reason_code);
CREATE INDEX IF NOT EXISTS ix_downtime_reasons_tenant_active
    ON downtime_reasons (tenant_id, active_flag);
CREATE INDEX IF NOT EXISTS ix_downtime_reasons_station
    ON downtime_reasons (tenant_id, station_scope_value);

INSERT INTO downtime_reasons
    (tenant_id, reason_code, reason_name, reason_group,
     planned_flag, default_block_mode, requires_comment,
     requires_supervisor_review, active_flag, sort_order)
VALUES
    ('default', 'PLANNED_MAINT',     'Planned maintenance',    'PLANNED_STOP', TRUE,  'BLOCK', FALSE, FALSE, TRUE, 10),
    ('default', 'BREAKDOWN_GENERIC', 'Equipment breakdown',    'BREAKDOWN',    FALSE, 'BLOCK', TRUE,  FALSE, TRUE, 20),
    ('default', 'MATERIAL_SHORTAGE', 'Material shortage',      'MATERIAL',     FALSE, 'BLOCK', TRUE,  FALSE, TRUE, 30),
    ('default', 'QUALITY_HOLD',      'Quality hold',           'QUALITY',      FALSE, 'BLOCK', TRUE,  TRUE,  TRUE, 40),
    ('default', 'CHANGEOVER',        'Changeover',             'CHANGEOVER',   TRUE,  'BLOCK', FALSE, FALSE, TRUE, 50),
    ('default', 'UTILITIES_OUTAGE',  'Utilities outage',       'UTILITIES',    FALSE, 'BLOCK', TRUE,  FALSE, TRUE, 60),
    ('default', 'OTHER',             'Other',                  'OTHER',        FALSE, 'BLOCK', TRUE,  FALSE, TRUE, 90)
ON CONFLICT (tenant_id, reason_code) DO NOTHING;
