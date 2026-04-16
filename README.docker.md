# Docker Setup for MES Project

This project now uses a single root `docker-compose.yml` for the full MES stack:

- PostgreSQL database
- FastAPI backend
- Vite frontend served by nginx
- CloudBeaver for DB inspection

## Prerequisites

- Docker and Docker Compose installed

## Start the Full Stack

From the repository root, run:

```bash
cd /workspaces/FleziBCG
docker compose up --build
```

This starts:

- `db` on port `5432`
- `backend` on port `8010`
- `frontend` on port `80`
- `cloudbeaver` on port `8978`

Access points:

- MES UI: `http://localhost`
- Backend API: `http://localhost:8010`
- CloudBeaver: `http://localhost:8978`

## Service Behavior

- The backend connects to PostgreSQL through the Compose network using service name `db`.
- The frontend calls the backend through nginx reverse proxy under `/api`.
- Startup order is readiness-based:
	- `backend` waits for healthy `db`
	- `frontend` waits for healthy `backend`
	- `cloudbeaver` waits for healthy `db`

## Database Persistence

PostgreSQL data is preserved in the existing Docker volume `docker_postgres_data`.

This is intentionally kept as an external volume so existing MES data is not recreated or reset.

## CloudBeaver Login

Open `http://localhost:8978`

CloudBeaver login:

- User: `flelibcg`
- Pass: `beniceSCM2026`

Then add the PostgreSQL connection:

- Host: `db`
- Port: `5432`
- Database: `mes`
- User: `mes`
- Password: `mes`

## Seeding

No seed scripts are run automatically by Docker Compose.

If you need seed or verification flows, run them manually from the backend environment.

## Stop the Stack

To stop the services:

```bash
docker compose down
```

This stops containers but does not delete the external PostgreSQL volume.

## Safe Recovery

If Docker leaves stale backend or frontend runtime state behind, the safe recovery is:

```bash
docker rm -f flezibcg-backend-1 flezibcg-frontend-1
docker compose up -d
```

This does not touch the database container data volume.