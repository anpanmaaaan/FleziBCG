# Quality PR Documentation Sync Checklist

Use this checklist for every Quality-related PR to keep docs aligned with code.

## 1. Scope and intent

- [ ] PR states exactly which Quality behavior changed (measurement, evaluation, hold, disposition, gating, accepted-good impact)
- [ ] PR states whether the change is behavior, contract, or internal-only
- [ ] PR confirms backend remains source of truth for quality outcomes

## 2. Design truth alignment

- [ ] Reviewed docs/design/02_domain/quality/quality-domain-contracts.md
- [ ] Reviewed docs/design/02_domain/quality/business-truth-quality-lite.md
- [ ] If execution interaction changed, reviewed docs/design/02_domain/execution/business-truth-station-execution-v4.md
- [ ] Any intended deviation is explicitly documented with rationale and follow-up

## 3. API and schema documentation

- [ ] Updated endpoint/request/response/error docs for all API contract changes
- [ ] Updated migration notes for table/column/constraint changes
- [ ] Documented tenant/scope/auth constraints for new or changed Quality actions
- [ ] Documented event names and payload changes when eventing changed

## 4. Behavior documentation

- [ ] Documented pass/fail/hold evaluation behavior
- [ ] Documented disposition ownership and allowed actor roles
- [ ] Documented quality-to-execution gate effects on allowed actions
- [ ] Documented quantity semantics (reported good, accepted good, hold, scrap)

## 5. Frontend contract sync (if UI touched)

- [ ] Updated UI docs for backend-authoritative quality truth
- [ ] Updated screen notes for shell/mock to integrated behavior transitions
- [ ] Updated en/ja i18n keys in the same PR when text keys changed

## 6. Tests and evidence

- [ ] Added/updated tests for changed Quality behavior
- [ ] Added/updated authz and tenant isolation tests for changed flows
- [ ] Added/updated quality-execution integration tests where relevant
- [ ] Included executed verification commands and outcomes in PR evidence

## 7. Same-PR docs gate

- [ ] Docs and code are both complete in this PR
- [ ] Reviewer explicitly confirmed docs-to-code alignment
- [ ] Any deferred docs have a linked follow-up with owner and target phase