from app.models.quality import (
    QualityGateDefinitionStatusEnum,
    QualityGateInstanceStatusEnum,
    QualityGateTypeEnum,
)


def test_quality_gate_definition_status_vocab_is_stable():
    assert {v.value for v in QualityGateDefinitionStatusEnum} == {
        "DRAFT",
        "ACTIVE",
        "RETIRED",
    }


def test_quality_gate_type_vocab_is_stable():
    assert {v.value for v in QualityGateTypeEnum} == {"PRE_ACCEPTANCE"}


def test_quality_gate_instance_status_vocab_is_stable():
    assert {v.value for v in QualityGateInstanceStatusEnum} == {
        "PENDING_MEASUREMENT",
        "PENDING_EVALUATION",
        "PASSED",
        "HOLD_ACTIVE",
        "DEVIATION_PENDING",
        "RECHECK_REQUIRED",
        "RELEASED",
        "CLOSED",
    }
