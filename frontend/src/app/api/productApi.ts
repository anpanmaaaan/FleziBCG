import { request } from "./httpClient";

export interface ProductItemFromAPI {
  product_id: string;
  tenant_id: string;
  product_code: string;
  product_name: string;
  product_type: string;
  lifecycle_status: string;
  description?: string | null;
  display_metadata?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

const BASE_PATH = "/v1/products";

export const productApi = {
  listProducts(signal?: AbortSignal) {
    return request<ProductItemFromAPI[]>(BASE_PATH, { signal });
  },

  getProduct(productId: string, signal?: AbortSignal) {
    return request<ProductItemFromAPI>(`${BASE_PATH}/${encodeURIComponent(productId)}`, { signal });
  },
};
