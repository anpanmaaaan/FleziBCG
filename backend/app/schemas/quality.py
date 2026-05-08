from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QualityMeasurementInput(BaseModel):
    item_code: str
    measured_value: float

    model_config = ConfigDict(extra="forbid")

    @field_validator("item_code")
    @classmethod
    def _item_code_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("item_code must be a non-blank string")
        return stripped


class QualityMeasurementSubmitRequest(BaseModel):
    operation_id: int
    measurements: list[QualityMeasurementInput] = Field(min_length=1)

    model_config = ConfigDict(extra="forbid")


class QualityRequirementItem(BaseModel):
    item_code: str
    label: str
    input_type: str
    required: bool = True
    unit: str | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None


class QualityOperationRequirementsResponse(BaseModel):
    operation_id: int
    operation_number: str
    operation_name: str
    qc_required: bool
    template_code: str | None = None
    template_name: str | None = None
    template_version: str | None = None
    items: list[QualityRequirementItem] = []


class QualityMeasurementValueResult(BaseModel):
    item_code: str
    measured_value: float
    lower_limit: float | None = None
    upper_limit: float | None = None
    is_within_spec: bool


class QualityMeasurementSubmitResponse(BaseModel):
    measurement_record_id: int
    operation_id: int
    quality_status: str
    review_status: str
    accepted_good_release_qty: int = 0
    held_pending_good_qty: int = 0
    hold_id: int | None = None
    submitted_at: datetime
    values: list[QualityMeasurementValueResult]


class QualityHoldItem(BaseModel):
    hold_id: int
    operation_id: int
    operation_number: str
    measurement_record_id: int
    status: str
    review_status: str
    reason: str
    created_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QualityDispositionRequest(BaseModel):
    disposition_code: str
    comment: str | None = None

    @field_validator("disposition_code")
    @classmethod
    def _disposition_code_not_blank(cls, value: str) -> str:
        stripped = value.strip().upper()
        if not stripped:
            raise ValueError("disposition_code must be a non-blank string")
        return stripped


class QualityDispositionResponse(BaseModel):
    hold_id: int
    disposition_decision_id: int
    disposition_code: str
    quality_status: str
    review_status: str
    hold_status: str
    accepted_good_release_qty: int = 0
    held_pending_good_qty: int = 0
    decided_by: str
    decided_at: datetime
