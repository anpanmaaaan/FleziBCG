import { request } from "./httpClient";

export interface QualityMeasurementInput {
  item_code: string;
  measured_value: number;
}

export interface QualityRequirementItem {
  item_code: string;
  label: string;
  input_type: string;
  required: boolean;
  unit: string | null;
  lower_limit: number | null;
  upper_limit: number | null;
}

export interface QualityOperationRequirementsResponse {
  operation_id: number;
  operation_number: string;
  operation_name: string;
  qc_required: boolean;
  template_code: string | null;
  template_name: string | null;
  template_version: string | null;
  items: QualityRequirementItem[];
}

export interface QualityMeasurementSubmitRequest {
  operation_id: number;
  gate_instance_id?: number;
  measurements: QualityMeasurementInput[];
}

export interface QualityMeasurementValueResult {
  item_code: string;
  measured_value: number;
  lower_limit: number | null;
  upper_limit: number | null;
  is_within_spec: boolean;
}

export interface QualityMeasurementSubmitResponse {
  measurement_record_id: number;
  operation_id: number;
  gate_instance_id: number | null;
  quality_status: string;
  review_status: string;
  accepted_good_release_qty: number;
  held_pending_good_qty: number;
  hold_id: number | null;
  submitted_at: string;
  values: QualityMeasurementValueResult[];
}

export interface QualityHoldItem {
  hold_id: number;
  operation_id: number;
  operation_number: string;
  measurement_record_id: number;
  status: string;
  review_status: string;
  reason: string;
  created_by: string;
  created_at: string;
}

export interface QualityDispositionRequest {
  disposition_code: "RELEASE_QC_HOLD" | "ACCEPT_WITH_DEVIATION" | "REQUIRE_RECHECK" | "CONFIRM_SCRAP";
  comment?: string | null;
}

export interface QualityDispositionResponse {
  hold_id: number;
  disposition_decision_id: number;
  disposition_code: string;
  quality_status: string;
  review_status: string;
  hold_status: string;
  accepted_good_release_qty: number;
  held_pending_good_qty: number;
  decided_by: string;
  decided_at: string;
}

export interface QualityDeviationRequestCreate {
  reason: string;
}

export interface QualityDeviationRequestItem {
  deviation_request_id: number;
  hold_id: number;
  gate_instance_id: number | null;
  status: string;
  requested_by: string;
  reason: string;
  requested_at: string;
  resolved_by: string | null;
  resolved_at: string | null;
  resolution_comment: string | null;
}

export interface QualityDeviationResolveRequest {
  resolution_status: "APPROVED" | "REJECTED" | "CLOSED";
  resolution_comment?: string | null;
}

export interface QualityNonconformanceCreateRequest {
  operation_id: number;
  nc_code: string;
  hold_id?: number;
  severity: string;
  description: string;
}

export interface QualityNonconformanceItem {
  nonconformance_id: number;
  nc_code: string;
  operation_id: number;
  hold_id: number | null;
  status: string;
  severity: string;
  description: string;
  disposition_code: string | null;
  reported_by: string;
  created_at: string;
  updated_at: string;
}

export interface QualityGateDefinitionCreateRequest {
  code: string;
  name: string;
  gate_type: string;
  rule_set_version: string;
  applicability_scope_type: string;
  applicability_scope_value: string;
}

export interface QualityGateDefinitionResponse {
  gate_definition_id: number;
  code: string;
  name: string;
  status: string;
  gate_type: string;
  rule_set_version: string;
  applicability_scope_type: string;
  applicability_scope_value: string;
  tenant_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface QualityGateInstanceOpenRequest {
  operation_id: number;
  gate_definition_id: number;
}

export interface QualityGateInstanceResponse {
  gate_instance_id: number;
  gate_definition_id: number;
  operation_id: number;
  status: string;
  review_status: string;
  opened_by: string;
  closed_by: string | null;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

export const qualityApi = {
  getRequirements(operationId: number) {
    return request<QualityOperationRequirementsResponse>(
      `/v1/quality/operations/${encodeURIComponent(String(operationId))}/requirements`
    );
  },

  submitMeasurement(payload: QualityMeasurementSubmitRequest) {
    return request<QualityMeasurementSubmitResponse>("/v1/quality/measurements", {
      method: "POST",
      body: payload,
    });
  },

  listHolds() {
    return request<QualityHoldItem[]>("/v1/quality/holds");
  },

  listDeviations() {
    return request<QualityDeviationRequestItem[]>("/v1/quality/deviations");
  },

  requestDeviation(holdId: number, payload: QualityDeviationRequestCreate) {
    return request<QualityDeviationRequestItem>(
      `/v1/quality/holds/${encodeURIComponent(String(holdId))}/deviations`,
      {
        method: "POST",
        body: payload,
      }
    );
  },

  resolveDeviation(
    deviationRequestId: number,
    payload: QualityDeviationResolveRequest
  ) {
    return request<QualityDeviationRequestItem>(
      `/v1/quality/deviations/${encodeURIComponent(String(deviationRequestId))}/resolve`,
      {
        method: "POST",
        body: payload,
      }
    );
  },

  listNonconformances() {
    return request<QualityNonconformanceItem[]>("/v1/quality/nonconformances");
  },

  createNonconformance(payload: QualityNonconformanceCreateRequest) {
    return request<QualityNonconformanceItem>("/v1/quality/nonconformances", {
      method: "POST",
      body: payload,
    });
  },

  recordDisposition(holdId: number, payload: QualityDispositionRequest) {
    return request<QualityDispositionResponse>(
      `/v1/quality/reviews/${encodeURIComponent(String(holdId))}/disposition`,
      {
        method: "POST",
        body: payload,
      }
    );
  },

  listGateDefinitions() {
    return request<QualityGateDefinitionResponse[]>("/v1/quality/gates/definitions");
  },

  createGateDefinition(payload: QualityGateDefinitionCreateRequest) {
    return request<QualityGateDefinitionResponse>("/v1/quality/gates/definitions", {
      method: "POST",
      body: payload,
    });
  },

  openGateInstance(payload: QualityGateInstanceOpenRequest) {
    return request<QualityGateInstanceResponse>("/v1/quality/gates/instances/open", {
      method: "POST",
      body: payload,
    });
  },
};
