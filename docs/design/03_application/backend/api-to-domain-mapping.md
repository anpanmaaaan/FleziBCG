# API to Domain Mapping (v4)

## Flow
API → Command → Validation → State → Event → Projection

## Example: Start Execution
POST /execution/{id}/start
Command: StartExecution
State: NOT_STARTED → RUNNING
Event: execution.started

## Example: Submit QC
POST /quality/{id}/submit
Command: SubmitQC
State: QC_PENDING → QC_PASSED / FAILED
Event:
- qc_submitted
- qc_result

## Rules
- No business logic in API
- All transitions via domain
- All writes emit event
