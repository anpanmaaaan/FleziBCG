from app.models.quality import (
    QualityDispositionCatalog,
    QualityDeviationRequest,
    QualityDeviationRequestStatusEnum,
    QualityNonconformance,
    QualityNonconformanceStatusEnum,
    QualityRuleDefinition,
    QualityRuleSet,
    QualityApplicabilityPolicy,
)


def test_quality_policy_model_tablenames_are_stable():
    assert QualityApplicabilityPolicy.__tablename__ == "quality_applicability_policies"
    assert QualityRuleSet.__tablename__ == "quality_rule_sets"
    assert QualityRuleDefinition.__tablename__ == "quality_rule_definitions"
    assert QualityDispositionCatalog.__tablename__ == "quality_disposition_catalog"
    assert QualityDeviationRequest.__tablename__ == "quality_deviation_requests"
    assert QualityNonconformance.__tablename__ == "quality_nonconformances"


def test_quality_policy_model_core_columns_exist():
    applicability_cols = set(QualityApplicabilityPolicy.__table__.columns.keys())
    assert {"policy_code", "scope_type", "scope_value", "qc_required", "tenant_id"}.issubset(
        applicability_cols
    )

    rule_set_cols = set(QualityRuleSet.__table__.columns.keys())
    assert {"rule_set_code", "rule_set_version", "tenant_id"}.issubset(rule_set_cols)

    rule_def_cols = set(QualityRuleDefinition.__table__.columns.keys())
    assert {"rule_set_id", "item_code", "evaluation_operator", "required"}.issubset(
        rule_def_cols
    )

    disposition_cols = set(QualityDispositionCatalog.__table__.columns.keys())
    assert {
        "disposition_code",
        "requires_quality_approval",
        "releases_hold",
        "quality_status_target",
        "review_status_target",
        "tenant_id",
    }.issubset(disposition_cols)

    deviation_cols = set(QualityDeviationRequest.__table__.columns.keys())
    assert {"hold_id", "status", "requested_by", "reason", "tenant_id"}.issubset(
        deviation_cols
    )

    nc_cols = set(QualityNonconformance.__table__.columns.keys())
    assert {
        "nc_code",
        "operation_id",
        "status",
        "severity",
        "description",
        "tenant_id",
    }.issubset(nc_cols)


def test_quality_policy_status_vocab_for_deviation_and_nonconformance_is_stable():
    assert {v.value for v in QualityDeviationRequestStatusEnum} == {
        "OPEN",
        "APPROVED",
        "REJECTED",
        "CLOSED",
    }
    assert {v.value for v in QualityNonconformanceStatusEnum} == {
        "OPEN",
        "UNDER_REVIEW",
        "DISPOSITIONED",
        "CLOSED",
    }
