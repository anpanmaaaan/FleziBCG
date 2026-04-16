# DB-Only Stack

This folder defines the database-only Docker stack:
- PostgreSQL on port 5432
- CloudBeaver Community on port 8978

## Start

```bash
docker compose -f docker/docker-compose.db.yml up -d
```

## Stop

```bash
docker compose -f docker/docker-compose.db.yml down
```

## Reset DB completely

```bash
docker compose -f docker/docker-compose.db.yml down -v
```

This removes the PostgreSQL named volume and resets database contents.

## Recreate DB and seed

Current repo state does not include a checked-in Alembic configuration.
Use the existing schema init step, then run the deterministic seed set:

```bash
docker compose -f docker/docker-compose.db.yml up -d
cd backend
/workspaces/FleziBCG/.venv/bin/python -m app.db.init_db
/workspaces/FleziBCG/.venv/bin/python -m scripts.seed.seed_all
```

## Backend env source

Backend reads Postgres env values from:
- docker/.env.db
- backend/.env

For local backend execution outside Docker, host access is:
- Host: localhost
- Port: 5432

## CloudBeaver access

Open in Codespaces/browser:
- http://localhost:8978

Codespaces ports to forward:
- 8978 for CloudBeaver
- 5432 for PostgreSQL if you want direct local inspection tools

### Initial admin setup

On first open, CloudBeaver shows its local configuration wizard.
Create the local admin user there. No external auth is configured.

### Add PostgreSQL connection inside CloudBeaver

Use these values:
- Host: db
- Port: 5432
- Database: value of POSTGRES_DB from docker/.env.db
- User: value of POSTGRES_USER from docker/.env.db
- Password: value of POSTGRES_PASSWORD from docker/.env.db

After schema init and seeding, you should see:
- production_orders
- work_orders
- operations
- execution_events
