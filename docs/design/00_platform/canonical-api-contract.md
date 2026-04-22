# CANONICAL API CONTRACT

## Purpose
Defines API boundary rules for MOM Lite.

---

## Principles
- Backend is source of truth
- Responses return codes/enums, not localized text
- Datetime: ISO 8601 (UTC)
- Stable contracts; changes require contract PR

---

## Standard Response Shapes

### Success
{
  "data": { ... },
  "meta": { "request_id": "..." }
}

### Error
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable"
  }
}

---

## Pagination
{
  "data": [ ... ],
  "page": 1,
  "page_size": 50,
  "total": 120
}

---

## Filtering/Sorting
- query params: ?page=1&page_size=50&sort=created_at:desc&filter=status:RUNNING

---

## Compatibility
- Additive changes allowed (optional fields)
- Breaking changes require versioning and contract PR
