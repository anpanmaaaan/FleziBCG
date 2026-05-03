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
## Stale container — port binding lost after host restart
```
If the DB container exists from a previous run but was not started via
`docker compose up` (e.g., auto-started by Docker Desktop, or started via
`docker start`), Docker does **not** re-read the `ports:` spec.  The container
will show only `5432/tcp` (EXPOSE only) instead of `0.0.0.0:5432->5432/tcp`
(host-bound), and the backend/pytest will get `Connection refused`.

**Fix:**
## Reset DB completely
```bash
docker compose -f docker/docker-compose.db.yml up -d --force-recreate db
```

This tears down and recreates **only the `db` container** (data volume is
preserved), binding port 5432 to all host interfaces.
```bash
**Verify:**
docker compose -f docker/docker-compose.db.yml down -v
```bash
docker ps   # should show 0.0.0.0:5432->5432/tcp next to flezi-dev-db
```
```
> Note: the root `docker-compose.yml` creates a container named
> `flezibcg-db-1`.  The dev-tools compose (`docker/docker-compose.db.yml`)
> creates `flezi-dev-db` with a custom `container_name`.  Either container
> binds port 5432 to the host when started via `docker compose up`.

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
