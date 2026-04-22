from pydantic import BaseModel, ConfigDict


class DowntimeReasonItem(BaseModel):
    # Fields mirror the DB-backed master data. Classification (`reason_group`)
    # is surfaced so the FE can display grouping/labels if desired, but
    # selection and submission is on `reason_code` only.
    reason_code: str
    reason_name: str
    reason_group: str
    planned_flag: bool
    requires_comment: bool
    requires_supervisor_review: bool

    model_config = ConfigDict(from_attributes=True)
