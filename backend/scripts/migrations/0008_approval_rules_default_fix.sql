-- Tier 1 v2 compatibility: ensure approval_rules has non-null default for is_active

ALTER TABLE approval_rules ALTER COLUMN is_active SET DEFAULT TRUE;
UPDATE approval_rules SET is_active = TRUE WHERE is_active IS NULL;
