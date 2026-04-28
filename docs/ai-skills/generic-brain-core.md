# Generic Brain Core

Rules:
- define source of truth
- service/application layer owns business logic
- controllers/routes stay thin
- repositories are persistence-only
- UI is interaction, not business truth
- authn and authz are separate
- server-side authorization
- critical invariants beyond UI validation
- behavior-focused tests
- small reviewable changes
