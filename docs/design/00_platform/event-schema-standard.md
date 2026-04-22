# Event Schema Standard (v4)

{
  "event_id": "uuid",
  "event_type": "EXECUTION_STARTED",
  "timestamp": "ISO8601",
  "actor": {
    "operator_id": "...",
    "role": "OPERATOR"
  },
  "entity": {
    "execution_id": "...",
    "operation_id": "...",
    "work_order_id": "..."
  },
  "payload": {},
  "correlation_id": "...",
  "causation_id": "..."
}
