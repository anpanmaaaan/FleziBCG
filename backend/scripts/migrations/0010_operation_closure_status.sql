ALTER TABLE operations
ADD COLUMN IF NOT EXISTS closure_status VARCHAR(16);

UPDATE operations
SET closure_status = 'OPEN'
WHERE closure_status IS NULL OR closure_status = '';

ALTER TABLE operations
ALTER COLUMN closure_status SET DEFAULT 'OPEN';

ALTER TABLE operations
ALTER COLUMN closure_status SET NOT NULL;
