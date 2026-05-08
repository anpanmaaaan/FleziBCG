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

  recordDisposition(holdId: number, payload: QualityDispositionRequest) {
    return request<QualityDispositionResponse>(
      `/v1/quality/reviews/${encodeURIComponent(String(holdId))}/disposition`,
      {
        method: "POST",
        body: payload,
      }
    );
  },
};
