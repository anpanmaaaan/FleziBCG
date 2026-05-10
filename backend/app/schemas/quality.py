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
    gate_instance_id: int | None = None
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
    gate_instance_id: int | None = None
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


class QualityGateDefinitionCreateRequest(BaseModel):
    code: str
    name: str
    gate_type: str = "PRE_ACCEPTANCE"
    rule_set_version: str
    applicability_scope_type: str
    applicability_scope_value: str

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "code",
        "name",
        "rule_set_version",
        "applicability_scope_type",
        "applicability_scope_value",
    )
    @classmethod
    def _non_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must be non-blank")
        return stripped


class QualityGateDefinitionResponse(BaseModel):
    gate_definition_id: int
    code: str
    name: str
    status: str
    gate_type: str
    rule_set_version: str
    applicability_scope_type: str | None = None
    applicability_scope_value: str | None = None
    tenant_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class QualityGateInstanceOpenRequest(BaseModel):
    operation_id: int
    gate_definition_id: int

    model_config = ConfigDict(extra="forbid")


class QualityGateInstanceResponse(BaseModel):
    gate_instance_id: int
    gate_definition_id: int
    operation_id: int
    status: str
    review_status: str
    opened_by: str
    closed_by: str | None = None
    tenant_id: str
    created_at: datetime
    updated_at: datetime


class QualityDeviationRequestCreate(BaseModel):
    reason: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("reason")
    @classmethod
    def _reason_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("reason must be a non-blank string")
        return stripped


class QualityDeviationResolveRequest(BaseModel):
    resolution_status: str
    resolution_comment: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("resolution_status")
    @classmethod
    def _resolution_status_not_blank(cls, value: str) -> str:
        stripped = value.strip().upper()
        if not stripped:
            raise ValueError("resolution_status must be a non-blank string")
        return stripped


class QualityDeviationRequestItem(BaseModel):
    deviation_request_id: int
    hold_id: int
    gate_instance_id: int | None = None
    status: str
    requested_by: str
    reason: str
    requested_at: datetime
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    resolution_comment: str | None = None


class QualityNonconformanceCreateRequest(BaseModel):
    operation_id: int
    nc_code: str
    hold_id: int | None = None
    severity: str
    description: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("nc_code", "severity", "description")
    @classmethod
    def _non_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must be non-blank")
        return stripped


class QualityNonconformanceItem(BaseModel):
    nonconformance_id: int
    nc_code: str
    operation_id: int
    hold_id: int | None = None
    status: str
    severity: str
    description: str
    disposition_code: str | None = None
    reported_by: str
    created_at: datetime
    updated_at: datetime
