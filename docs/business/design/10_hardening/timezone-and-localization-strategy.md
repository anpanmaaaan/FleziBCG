# Timezone and Localization Strategy — FleziBCG MOM Platform

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-26 | v1.0 | Added timezone and localization ADR after CD Review 1 noted HRD-026 was only WATCH and not a real ADR. |

## Status

**P1-HARDENING ADR.**

This ADR does not block P0-A Foundation Database implementation, but it must be respected before implementing shift calendar, OEE by shift, multi-country deployment, or Japan-focused localization.

---

## 1. Decision

FleziBCG uses:

```text
UTC for persisted instants
plant timezone for production calendars and shift boundary resolution
user or plant display timezone depending screen context
i18n keys for UI text, never hard-coded business-facing strings
```

---

## 2. Timestamp Storage Rule

All persisted business/event timestamps that represent an instant must be stored as UTC-capable timestamps, preferably `timestamptz` in PostgreSQL.

Examples:

- `occurred_at`
- `recorded_at`
- `started_at`
- `ended_at`
- `created_at`
- `updated_at`
- `posted_at`
- `received_at`

Do not persist local-time-only strings for operational truth.

---

## 3. Plant Timezone Rule

Each plant must have a canonical IANA timezone, e.g.:

```text
Asia/Tokyo
Asia/Bangkok
Europe/Paris
America/New_York
```

The plant timezone is used for:

- production calendar;
- shift start/end resolution;
- OEE by shift/day/week;
- downtime and production reports by local plant day;
- cross-midnight shift assignment.

---

## 4. Display Timezone Rule

| Screen Type | Default Display Timezone |
|---|---|
| Station Execution | Plant timezone |
| Supervisory plant/line dashboard | Plant timezone |
| Quality operation screens | Plant timezone |
| Reports by plant/line/station | Plant timezone |
| User session/security screens | User preference or tenant default |
| Integration timestamps | UTC + plant/user formatted display where useful |
| Audit export | UTC canonical timestamp plus optional local display column |

Frontend may format timestamps, but backend must provide enough context to avoid ambiguous local time.

---

## 5. Shift and Cross-Midnight Rule

Shift membership is resolved by plant timezone.

A shift crossing midnight belongs to the configured shift business date, not automatically the calendar date of every timestamp.

Example:

```text
Night shift: 22:00-06:00 Asia/Tokyo
Business date rule: shift_start_date
Event at 2026-04-27 01:30 JST belongs to the 2026-04-26 night shift
```

The exact business-date rule must be configured by plant/tenant before OEE-by-shift is productionized.

---

## 6. DST Rule

For plants in DST-observing regions:

- store all instants in UTC;
- calculate local display using IANA timezone rules;
- do not assume all shifts are exactly 8 or 12 clock hours during DST transitions;
- production calendar must handle missing/repeated local times explicitly.

If the first target market is Japan, DST is less urgent, but the platform must not hard-code no-DST assumptions.

---

## 7. Localization Rule

UI text must use i18n keys.

Current localization baseline:

```text
en.ts and ja.ts must remain key-synchronized
```

Rules:

- no hard-coded operator-facing production text;
- no hard-coded Japanese/English strings in backend error payload except stable machine-readable codes;
- API errors use stable `code`, frontend maps to localized text;
- names, product codes, lot codes, and comments must be UTF-8 safe;
- CSV/export encoding must be explicitly selected when Japanese customer workflows require Shift-JIS compatibility.

---

## 8. Calendar / Holiday Rule

Holiday calendars are plant/tenant configuration, not hard-coded country logic.

Japan calendar support may be provided through tenant/plant configured calendars rather than hard-coding national holidays in the core.

---

## 9. P0 / P1 Scope

| Phase | Requirement |
|---|---|
| P0-A | Store UTC timestamps; plant table should allow timezone field. |
| P0-B/P0-C | Execution events carry UTC timestamps; display can be simple. |
| P1 | Shift calendar and OEE must use plant timezone and cross-midnight shift rules. |
| P1/P2 | i18n key coverage and export encoding policy hardened for target customer. |

---

## 10. Anti-Patterns

| Anti-pattern | Why forbidden |
|---|---|
| Persisting local display time as truth | Ambiguous under timezone/DST changes. |
| Deriving shift by UTC date only | Wrong for plant-local shift reporting. |
| Hard-coding Japan timezone globally | Breaks multi-country deployment. |
| Hard-coding UI labels | Breaks i18n governance. |
| Treating user timezone as plant production timezone | Plant operations are plant-local by default. |

---

## 11. Final Decision

Timezone/localization is upgraded from `WATCH` to `P1-HARDENING`.

It does not block P0-A foundation implementation, but P0-A should include plant timezone field readiness so later shift/OEE/reporting work does not require destructive schema changes.
