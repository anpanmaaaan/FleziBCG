ALTER TABLE operations
ADD COLUMN IF NOT EXISTS reopen_count INTEGER;

UPDATE operations
SET reopen_count = 0
WHERE reopen_count IS NULL;

ALTER TABLE operations
ALTER COLUMN reopen_count SET DEFAULT 0;

ALTER TABLE operations
ALTER COLUMN reopen_count SET NOT NULL;

ALTER TABLE operations
ADD COLUMN IF NOT EXISTS last_reopened_at TIMESTAMP;

ALTER TABLE operations
ADD COLUMN IF NOT EXISTS last_reopened_by VARCHAR(128);

ALTER TABLE operations
ADD COLUMN IF NOT EXISTS last_closed_at TIMESTAMP;

ALTER TABLE operations
ADD COLUMN IF NOT EXISTS last_closed_by VARCHAR(128);
