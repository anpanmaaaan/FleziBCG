import { request } from "./httpClient";

export interface RoutingOperationItemFromAPI {
  operation_id: string;
  routing_id: string;
  operation_code: string;
  operation_name: string;
  sequence_no: number;
  standard_cycle_time?: number | null;
  required_resource_type?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RoutingItemFromAPI {
  routing_id: string;
  tenant_id: string;
  product_id: string;
  routing_code: string;
  routing_name: string;
  lifecycle_status: string;
  operations: RoutingOperationItemFromAPI[];
  created_at: string;
  updated_at: string;
}

const BASE_PATH = "/v1/routings";

export const routingApi = {
  listRoutings(signal?: AbortSignal) {
    return request<RoutingItemFromAPI[]>(BASE_PATH, { signal });
  },

  getRouting(routingId: string, signal?: AbortSignal) {
    return request<RoutingItemFromAPI>(`${BASE_PATH}/${encodeURIComponent(routingId)}`, { signal });
  },
};
