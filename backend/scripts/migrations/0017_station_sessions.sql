-- Migration: 0017_station_sessions.sql
-- Introduces: station_sessions table for P0-C-04B Station Session lifecycle foundation.
-- Notes:
-- - Claim remains compatibility layer and this migration does not alter claim tables.
-- - Partial unique index enforces one active OPEN station session per tenant+station.

CREATE TABLE IF NOT EXISTS station_sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    station_id VARCHAR(128) NOT NULL,
    operator_user_id VARCHAR(64),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    status VARCHAR(16) NOT NULL DEFAULT 'OPEN',
    equipment_id VARCHAR(128),
    current_operation_id INTEGER REFERENCES operations(id),
    event_name_status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_station_sessions_status
        CHECK (status IN ('OPEN', 'CLOSED'))
);

CREATE INDEX IF NOT EXISTS ix_station_sessions_tenant_id ON station_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS ix_station_sessions_station_id ON station_sessions(station_id);
CREATE INDEX IF NOT EXISTS ix_station_sessions_operator_user_id ON station_sessions(operator_user_id);
CREATE INDEX IF NOT EXISTS ix_station_sessions_status ON station_sessions(status);
CREATE INDEX IF NOT EXISTS ix_station_sessions_current_operation_id ON station_sessions(current_operation_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_station_sessions_tenant_station_active_open
    ON station_sessions(tenant_id, station_id)
    WHERE status = 'OPEN' AND closed_at IS NULL;
