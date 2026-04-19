# Station Execution Policy and Master Data (v1, Canonical)

Status: Authoritative configuration and policy reference (v1)  
Owner: Product / Domain / Operations / Architecture  
Primary consumers: Backend, Frontend, QA, Solution Design, Implementation, Plant Configuration  
Scope: Station execution core only  
Depends on:
- `business-truth-station-execution.md`
- `station-execution-state-matrix.md`
- `station-execution-command-event-contracts.md`
- `station-execution-authorization-matrix.md`
- `station-execution-exception-and-approval-matrix.md`
- `station-execution-operational-sop.md`

---

# 1. Purpose

This document defines the **configuration, policy, and master data layer** required to run station execution without hard-coding business rules in frontend or backend services.

It answers:

- which rules are data-driven versus code-driven
- which master data must exist before execution can be used safely
- which policy switches the backend evaluates during command validation and status derivation
- which entities are tenant-level, plant-level, line-level, station-level, operation-level, or global catalog data
- which defaults are acceptable in v1 and which are future-ready

This file does **not** replace business truth.  
It makes business truth implementable and configurable.

---

# 2. Core policy principles

## PMD-CORE-001 — Business truth stays in code + policy, not in UI logic

Frontend may render hints and disable buttons for UX, but all effective behavior must be validated server-side against configuration and policy.

## PMD-CORE-002 — Policy must be explicit

If behavior can differ by tenant / plant / process / station, it must be modeled explicitly as configuration, not implied by screen behavior or developer assumption.

## PMD-CORE-003 — Master data and runtime truth are different

Master data defines what *may* happen.  
Runtime event history defines what *did* happen.

## PMD-CORE-004 — Defaults must be safe, not permissive

When policy or configuration is missing:
- backend should reject unsafe write actions
- UI should surface configuration mismatch clearly
- implementers should not silently fall back to broad permissive behavior

## PMD-CORE-005 — Scope ownership matters

A policy value configured at a narrower scope overrides a broader-scope default only where override is explicitly allowed.

---

# 3. Configuration taxonomy

Station execution configuration is split into four categories:

## 3.1 Master data

Reference entities required for execution truth to make sense.

Examples:
- station
- work center / line / area / plant
- operation definition
- reason codes
- quality rule definitions
- capability mappings

## 3.2 Policy data

Boolean, numeric, enum, or rule values that change command acceptance or status derivation without changing domain code.

Examples:
- pause threshold before downtime classification is required
- whether report while paused is allowed
- whether manual close is enabled
- whether self-approval is blocked for a given exception type

## 3.3 Catalog data

Standardized codes used across runtime events.

Examples:
- downtime categories
- defect reasons
- exception types
- disposition codes

## 3.4 Runtime reference bindings

Assignments that connect master/policy/catalog objects to a concrete execution context.

Examples:
- station → capability profile
- operation → required quality rule set
- plant → default exception policy set
- station → session exclusivity policy

---

# 4. Required master data domains

The following master data domains should exist before station execution is considered production-safe.

## 4.1 Organization and scope master data

Minimum entities:
- tenant
- plant
- area
- line
- station
- equipment (optional in v1, but recommended)

Minimum fields:
- unique stable ID
- code
- name
- parent scope ID
- active flag
- effective dates if lifecycle tracking exists

## 4.2 Station master data

Each station should define at least:
- station ID
- station code / display name
- parent line / area / plant
- active flag
- station type
- concurrency mode
- session mode
- capability profile reference
- default execution policy set reference
- default downtime policy set reference
- default quality policy set reference
- local timezone if needed

### Recommended v1 fields
- `station_concurrency_mode`
  - `SINGLE_ACTIVE_EXECUTION`
- `station_session_mode`
  - `EXCLUSIVE_USER_SESSION`
  - `SHARED_STATION_SESSION` (future-oriented)
- `supports_manual_reporting`
- `supports_qc_measurement_entry`
- `supports_downtime_classification`

## 4.3 Operation definition master data

Each operation definition should define at least:
- operation definition ID
- code / name
- process family / type
- default unit of measure
- routing sequence metadata if relevant upstream
- compatible capability requirement
- default quantity policy set reference
- default quality policy set reference
- default completion policy set reference

## 4.4 Work order / operation runtime reference minimums

Although WO and operation runtime context live outside this document’s master-data scope, station execution depends on the runtime references being present:
- work order ID
- operation ID
- planned quantity
- unit of measure
- station assignment or eligibility
- dispatch / release status from orchestration layer

## 4.5 Reason catalogs

Required catalogs:
- downtime reason catalog
- defect reason catalog
- optional pause reason catalog
- optional reopen reason catalog

## 4.6 Quality catalogs

Required or strongly recommended:
- quality rule set catalog
- sample type catalog
- measurement type catalog
- quality disposition catalog

## 4.7 Exception catalogs

Required catalogs:
- exception type catalog
- disposition code catalog
- evidence requirement policy catalog

---

# 5. Scope and override model

## PMD-SCOPE-001 — Scope hierarchy

Configuration should be supportable across these levels:
- tenant
- plant
- area
- line
- station
- operation definition
- operation runtime binding (exceptional only)

## PMD-SCOPE-002 — Override order

Default override precedence should be:

1. runtime explicit override (rare, audited)
2. station-level override
3. line-level override
4. area-level override
5. plant-level override
6. tenant default
7. platform default

## PMD-SCOPE-003 — Not every policy is overridable everywhere

Each policy definition should explicitly state whether overrides are allowed and at which scope.

Example:
- `self_approval_allowed` should generally **not** be overridable at station level
- `pause_threshold_seconds` may be overridable at plant, line, or station level

---

# 6. Mandatory policy families

The following policy families should exist for station execution.

## 6.1 Session policy family

Controls station session behavior.

### Required policy keys
- `station_session_required` (bool)
- `exclusive_station_session` (bool)
- `allow_shift_handover_with_open_review` (bool)
- `allow_session_close_with_paused_execution` (bool)
- `allow_session_close_with_open_downtime` (bool)

### Recommended v1 defaults
- `station_session_required = true`
- `exclusive_station_session = true`
- `allow_shift_handover_with_open_review = false`
- `allow_session_close_with_paused_execution = false`
- `allow_session_close_with_open_downtime = false`

## 6.2 Execution policy family

Controls claim / start / pause / resume / complete behavior.

### Required policy keys
- `one_running_execution_per_station` (bool)
- `allow_claim_without_release` (bool)
- `allow_start_without_claim` (bool)
- `allow_report_while_paused` (bool)
- `allow_complete_with_open_review` (bool)
- `allow_complete_with_qc_pending` (bool)
- `allow_complete_with_open_downtime` (bool)

### Recommended v1 defaults
- `one_running_execution_per_station = true`
- `allow_claim_without_release = false`
- `allow_start_without_claim = false`
- `allow_report_while_paused = false` unless explicitly required
- `allow_complete_with_open_review = false`
- `allow_complete_with_qc_pending = false`
- `allow_complete_with_open_downtime = false`

## 6.3 Pause and downtime policy family

Controls when pause is acceptable and when downtime classification is required.

### Required policy keys
- `pause_threshold_seconds_before_reason_required`
- `downtime_required_after_pause_threshold` (bool)
- `allow_pause_without_reason` (bool)
- `allow_overlapping_downtime_intervals` (bool)
- `default_downtime_block_mode`
  - `SOFT`
  - `HARD`

### Recommended v1 defaults
- `pause_threshold_seconds_before_reason_required = 300`
- `downtime_required_after_pause_threshold = true`
- `allow_pause_without_reason = true` for short pause only
- `allow_overlapping_downtime_intervals = false`
- `default_downtime_block_mode = HARD` only for selected reason groups, not globally

## 6.4 Quantity policy family

Controls quantity acceptance, tolerance, and completion math.

### Required policy keys
- `allow_negative_quantity_delta` (bool)
- `allow_zero_quantity_report` (bool)
- `planned_qty_overrun_tolerance_type`
  - `ABSOLUTE`
  - `PERCENT`
- `planned_qty_overrun_tolerance_value`
- `allow_short_close_without_approval` (bool)
- `accepted_good_derivation_mode`
- `ng_reason_required_when_ng_reported` (bool)

### Recommended v1 defaults
- `allow_negative_quantity_delta = false`
- `allow_zero_quantity_report = false`
- `allow_short_close_without_approval = false`
- `ng_reason_required_when_ng_reported = true`

### Required v1 canonical rule
`accepted_good_derivation_mode` must be explicitly configured.

Recommended allowed modes for v1:
- `DIRECT_ON_REPORT_WHEN_NO_QC_GATE`
- `DEFERRED_UNTIL_QC_OR_DISPOSITION`

Do not leave this implied.

## 6.5 Quality policy family

Controls measurement submission, hold behavior, and accepted-good derivation.

### Required policy keys
- `quality_required` (bool)
- `quality_gate_mode`
  - `NONE`
  - `INLINE_REQUIRED`
  - `POST_REPORT_REQUIRED`
- `qc_fail_requires_hold` (bool)
- `qc_hold_blocks_resume` (bool)
- `qc_hold_blocks_completion` (bool)
- `accepted_good_release_on_disposition` (bool)
- `quality_disposition_owner_mode`
  - `QUALITY_ONLY`

### Recommended v1 defaults
- `quality_required = false` unless operation explicitly binds a quality rule set
- `quality_gate_mode = NONE` unless configured
- `qc_fail_requires_hold = true` when quality is mandatory
- `qc_hold_blocks_resume = true`
- `qc_hold_blocks_completion = true`
- `accepted_good_release_on_disposition = true` when `accepted_good_derivation_mode = DEFERRED_UNTIL_QC_OR_DISPOSITION`
- `quality_disposition_owner_mode = QUALITY_ONLY`

## 6.6 Exception and approval policy family

Controls exception behavior and approval ownership.

### Required policy keys
- `exception_review_required_by_type`
- `self_approval_allowed_by_type`
- `approval_owner_by_exception_type`
- `disposition_catalog_by_exception_type`
- `decision_more_info_enabled` (bool)
- `approval_expiry_enabled` (bool)
- `approval_expiry_seconds` (nullable)

### Recommended v1 defaults
- `self_approval_allowed_by_type = false` for all default exception types
- `decision_more_info_enabled = false` unless implemented end-to-end
- `approval_expiry_enabled = false` unless tokenized approval consumption exists

## 6.7 Closure and reopen policy family

Controls close / reopen behavior.

### Required policy keys
- `auto_close_enabled` (bool)
- `manual_close_allowed` (bool)
- `reopen_allowed` (bool)
- `reopen_requires_approval` (bool)
- `max_reopen_count` (nullable)
- `reopen_allowed_when_downstream_consumed` (bool)

### Recommended v1 defaults
- `auto_close_enabled = true` or `false` by plant policy, but choose one explicitly
- `manual_close_allowed = true`
- `reopen_allowed = true`
- `reopen_requires_approval = true`
- `max_reopen_count = null` or bounded by policy
- `reopen_allowed_when_downstream_consumed = false`

## 6.8 Support / impersonation policy family

Controls production actions by non-production roles.

### Required policy keys
- `support_session_required_for_admin_write` (bool)
- `support_session_required_for_ots_write` (bool)
- `production_write_allowed_for_adm` (bool)
- `production_write_allowed_for_ots` (bool)
- `support_reason_required` (bool)

### Recommended v1 defaults
- `support_session_required_for_admin_write = true`
- `support_session_required_for_ots_write = true`
- `production_write_allowed_for_adm = false` by default unless explicit support flow active
- `production_write_allowed_for_ots = false` by default unless explicit support flow active
- `support_reason_required = true`

---

# 7. Catalog definitions that must be canonical

These code lists should be centrally managed and reused consistently across services.

## 7.1 Exception type catalog

Canonical v1 exception types:
- `SHORT_CLOSE_REQUEST`
- `OVERRUN_REQUEST`
- `FORCE_COMPLETE_REQUEST`
- `FORCE_RESUME_REQUEST`
- `REOPEN_OPERATION_REQUEST`
- `BLOCK_OVERRIDE_REQUEST`
- `QC_HOLD_RELEASE_REQUEST`
- `QC_DEVIATION_ACCEPT_REQUEST`
- `QC_RECHECK_REQUEST`
- `SCRAP_DISPOSITION_REQUEST`
- `OTHER_REQUEST`

Do not create per-screen aliases.

## 7.2 Disposition code catalog

Canonical v1 disposition codes should include at least:
- `ALLOW_SHORT_CLOSE`
- `ALLOW_OVERRUN`
- `ALLOW_FORCE_COMPLETE`
- `ALLOW_FORCE_RESUME`
- `ALLOW_REOPEN`
- `ALLOW_BLOCK_OVERRIDE`
- `RELEASE_HOLD`
- `ACCEPT_WITH_DEVIATION`
- `RECHECK_REQUIRED`
- `SCRAP`

## 7.3 Decision outcomes

Canonical v1 decision outcomes:
- `APPROVED`
- `REJECTED`
- `MORE_INFO_REQUIRED` (only if implemented end-to-end)

## 7.4 Quality disposition codes

Quality projections may expose finer-grained `quality_disposition_code` values such as:
- `PASS`
- `FAIL`
- `RELEASE_HOLD`
- `ACCEPT_WITH_DEVIATION`
- `RECHECK_REQUIRED`
- `SCRAP`
- `QUARANTINE`

These are richer than coarse `quality_status` and should be preserved for audit and downstream logic.

---

# 8. Required bindings between master data and policy

The following bindings should exist in configuration.

## 8.1 Station → capability profile

Determines which operation types a station can run.

## 8.2 Operation definition → required capability profile

Determines station eligibility for the operation.

## 8.3 Station → session / execution policy sets

Determines how station session, pause, downtime, and concurrency behave.

## 8.4 Operation definition → quantity / quality / completion policy sets

Determines accepted-good logic, QC requirements, and completion conditions.

## 8.5 Plant or line → exception / approval policy set

Determines which exception types exist locally and who approves them.

## 8.6 Operation or product family → defect reason catalog subset

Optional in v1 but recommended to avoid irrelevant defect choices.

---

# 9. Accepted good policy: must be explicit

This is the most important policy area for station execution.

## PMD-QTY-001 — `accepted_good_qty` must not be guessed

The backend must not infer accepted-good behavior from UI flow alone.

## PMD-QTY-002 — Required policy question

For each operation or quality mode, the system must know:

**When does reported good become accepted good?**

## 9.1 Minimum v1 supported modes

### Mode A — `DIRECT_ON_REPORT_WHEN_NO_QC_GATE`

Use when:
- no QC gate is configured
- reported good can be accepted immediately

Behavior:
- `reported_good_qty` increases on accepted production report
- `accepted_good_qty` increases at the same time

### Mode B — `DEFERRED_UNTIL_QC_OR_DISPOSITION`

Use when:
- quality gate exists
- hold/disposition may delay acceptance

Behavior:
- `reported_good_qty` increases on production report
- `accepted_good_qty` remains unchanged until QC pass or authorized disposition releases quantity

## 9.2 Things that must be configured, not guessed

When deferred mode is used, the following must be defined by policy or process design:
- what quantity bucket is held pending QC
- whether QC applies to the entire reported batch, only a sample-linked bucket, or another lot construct
- whether `ACCEPT_WITH_DEVIATION` releases accepted good
- whether `SCRAP` converts quantity into NG / scrap bucket and removes it from releasable good

If these are not modeled yet, the implementation should start with a simpler operation-level hold assumption and document that constraint clearly.

---

# 10. Downtime and block policy

## PMD-DT-001 — Pause and downtime are related but not identical

Configuration must define when an open pause becomes unacceptable without classified downtime.

## PMD-DT-002 — Reason groups should define block behavior

Downtime reason groups should indicate whether they imply:
- no block
- soft block
- hard block

### Suggested downtime reason master fields
- `reason_code`
- `reason_name`
- `reason_group`
- `planned_flag`
- `default_block_mode`
- `requires_comment`
- `requires_supervisor_review`
- `active_flag`

## PMD-DT-003 — Overlapping downtime should remain disabled in v1

Keep v1 simple:
- one open downtime interval per execution context
- one effective blocking cause at a time for command validation

---

# 11. Quality policy and master data

## PMD-QC-001 — UI submits measurements, backend evaluates

Therefore the following must be configurable:
- which operations require quality input
- which measurements apply
- min/max / tolerance / rule type
- whether failure causes hold
- who owns the follow-up disposition path

## 11.1 Minimum quality rule master

Each quality rule set should define at least:
- quality rule set ID
- bound scope (operation definition / product family / station variant)
- measurement items
- rule evaluation type
- mandatory flag
- hold-on-fail flag
- sample rule reference if used
- active flag

## 11.2 Minimum measurement definition fields
- measurement code
- display name
- unit of measure
- value type (`NUMERIC`, `TEXT`, `BOOLEAN`, etc.)
- lower / upper bound if numeric
- decimal precision rule
- active flag

## 11.3 Default ownership in v1

Quality hold release and quality-owned disposition should remain owned by:
- `QCI`
- `QAL`

Do not broaden this ownership without explicit policy and governance review.

---

# 12. Authorization and policy interplay

## PMD-AUTH-001 — Role matrix alone is not enough

A user may have a role-level permission but still be blocked by policy.

Example:
- `SUP` can approve operational exceptions in principle
- but only if the exception type maps to supervisor ownership and SoD conditions pass

## PMD-AUTH-002 — Policy must not weaken SoD accidentally

Configuration must not allow local station admins to disable global separation-of-duties rules unless the platform explicitly supports that governance model.

## PMD-AUTH-003 — Missing policy should fail closed

If approval owner mapping or disposition catalog mapping is missing for an exception type, the backend should reject approval attempts rather than infer behavior.

---

# 13. Data persistence recommendations

The following data structures are recommended.

## 13.1 Master tables / config tables

Recommended logical tables:
- `station_master`
- `station_capability_profile`
- `operation_definition`
- `operation_capability_requirement`
- `reason_code_master`
- `defect_reason_master`
- `quality_rule_set`
- `quality_measurement_definition`
- `exception_type_master`
- `disposition_code_master`
- `policy_set`
- `policy_value`
- `policy_binding`

## 13.2 Runtime-reference bindings

Recommended logical bindings:
- `station_policy_binding`
- `operation_policy_binding`
- `plant_policy_binding`
- `exception_policy_binding`
- `quality_rule_binding`

## 13.3 Policy value style

Each policy value should define:
- policy key
- value type
- value
- scope level
- overrideable flag
- effective start / end date if versioning exists
- owner / changed by metadata

---

# 14. Seed data expectations for v1

A tenant / plant should not go live without at least:

- active plant / line / station hierarchy
- stations configured with execution policy set
- operation definitions bound to capability profile
- default quantity policy set
- default downtime reason catalog
- default defect reason catalog
- default exception type catalog
- default disposition code catalog
- explicit accepted-good derivation mode per relevant operation family
- explicit auto-close / manual-close / reopen settings

If any of these are missing, implementation teams should treat the plant as **not fully configured for execution truth**.

---

# 15. Backend expectations

Backend services should:
- resolve effective policy at command time
- validate configuration completeness before accepting critical commands
- derive statuses and unlock effects server-side
- reject commands when required policy data is missing
- surface machine-readable error codes for configuration gaps

### Example configuration-gap error cases
- station has no execution policy binding
- operation has no accepted-good derivation mode
- exception type has no decision owner mapping
- QC-required operation has no quality rule set

---

# 16. Frontend expectations

Frontend should:
- render the actions allowed by backend truth
- show user-facing explanations when configuration blocks an action
- avoid embedding business defaults not confirmed by backend
- support clear display of station / policy mismatch where possible

Frontend should **not**:
- invent fallback policy when backend returns a configuration error
- assume that all stations behave the same
- assume that all operations share the same quality or quantity behavior

---

# 17. QA expectations

QA should verify configuration-driven behavior explicitly.

Minimum QA themes:
- station with and without quality gate
- report while paused allowed vs disallowed
- short close approval required vs not required
- reopen blocked when downstream already consumed
- missing reason catalog mapping causes safe rejection
- missing accepted-good policy causes safe rejection
- support/admin write blocked without support session

---

# 18. What must exist now vs later

## 18.1 Must exist now

- station master with active flags and scope hierarchy
- operation definition with capability requirement
- downtime reason catalog
- defect reason catalog
- exception type catalog
- disposition code catalog
- station session policy
- execution policy
- quantity policy, including accepted-good derivation mode
- quality policy for operations that require QC
- close / reopen policy

## 18.2 Should be designed now, may be implemented later

- effective-dated policy versioning
- richer sample-plan logic
- lot-level accepted-good release logic
- fine-grained evidence requirement rules by exception type
- multi-lane / multi-slot station policy
- dynamic policy previews in admin UI

## 18.3 Can wait

- full policy simulation engine
- AI-assisted policy recommendation
- cross-plant policy benchmarking

---

# 19. Final implementation note

If implementers skip this policy/master-data layer and hard-code behavior directly into handlers, the station execution domain will become inconsistent across plants and difficult to govern.

The minimum safe approach is:
1. keep business truth in the canonical station execution docs
2. keep policy/configuration in explicit master data and policy tables
3. resolve effective policy on backend per command
4. derive statuses and effects from events + policy
5. reject unsafe behavior when configuration is incomplete
