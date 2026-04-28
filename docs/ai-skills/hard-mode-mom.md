# Hard Mode MOM

Strict rejection layer for FleziBCG MOM execution-critical work.

Turn ON when task touches execution state machine, command, event, projection truth, station/session/operator/equipment, production reporting, downtime, completion, quality hold, material/inventory execution impact, operational tenant/scope/auth, or critical invariant.

Reject if:
1. state machine is wrong
2. required event is missing
3. required invariant is missing
4. execution state is mutated directly
5. projection/read model is source of truth
6. frontend becomes execution or permission truth
7. tenant/scope/auth is not server-side
8. service layer is bypassed
9. critical invariant relies only on UI validation

Required pattern:
command → load context → validate tenant/scope/auth → validate state → validate invariants → emit event → update projection → return backend-derived result.
