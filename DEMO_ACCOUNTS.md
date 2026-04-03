# Demo Accounts

These are the pre-seeded demo accounts available in the MES Lite system. They are created automatically when the database is initialized.

## Account Credentials

| User ID | Username | Password | Role | Landing Page |
|---------|----------|----------|------|--------------|
| **adm-001** | admin | password123 | ADM (Admin) | Free roam (no default) |
| **pmg-001** | manager | password123 | PMG (Production Manager) | /dashboard |
| **sup-001** | supervisor | password123 | SUP (Supervisor) | /operations?lens=supervisor |
| **opr-001** | operator | password123 | OPR (Operator) | /station-execution |
| **qal-001** | qa | password123 | QAL (QA / Lines) | /operations?lens=qc |

## How to Login

1. Navigate to the login page: `/login`
2. Enter any **username** from the table above
3. Enter the password: `password123`
4. Click "Sign In"
5. You will be redirected to your role's default landing page

## Example Login

**Admin Account:**
- Username: `admin`
- Password: `password123`

**Operator Account:**
- Username: `operator`
- Password: `password123`

## Role Permissions

Each role grants different access levels:

| Role | Permissions | Purpose |
|------|-------------|---------|
| **ADM** | VIEW, ADMIN | Unrestricted system administration |
| **PMG** | VIEW, APPROVE | Production planning & approval authority |
| **SUP** | VIEW, EXECUTE | Shift leadership & execution oversight |
| **OPR** | EXECUTE | Station-level execution work |
| **QAL** | VIEW, APPROVE | Quality approval & sign-off |

## Integration with Seed Scenarios (S1–S4)

These demo accounts are used with the seed scenarios to test:
- **S1 (Normal Completion):** All users can view execution progress
- **S2 (Completed Late):** Dashboard shows delay metrics
- **S3 (Blocked Incident):** Supervisor lens highlights blocked operations
- **S4 (Variance Analysis):** IE/Process lens shows variance flags

## Impersonation (Admin Only)

The **admin** (adm-001) account can impersonate other roles for demo/support:

```
Admin impersonates Operator:
- Login as admin (adm-001 / password123)
- Create impersonation session for OPR role
- Execute work as if you're the operator
- Audit logs show real user (admin) + acting role (OPR)
```

## Notes

- **Development Only:** These credentials are for development and testing. Production deployments should not use these default accounts.
- **Tenant:** All accounts are in the "default" tenant
- **Email:** Demo accounts have example emails (admin@example.com, etc.)
- **Active:** All accounts are created with `is_active=true` and can log in immediately

## Resetting Accounts

If a demo account is locked or needs to be reset:

```bash
cd /workspaces/FleziBCG/backend
python -c "from app.db.init_db import init_db; init_db()"
```

This will re-seed all demo accounts with their original credentials.
