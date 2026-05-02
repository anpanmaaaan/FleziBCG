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

export interface ProductVersionItemFromAPI {
  product_version_id: string;
  tenant_id: string;
  product_id: string;
  version_code: string;
  version_name?: string | null;
  lifecycle_status: "DRAFT" | "RELEASED" | "RETIRED";
  is_current: boolean;
  effective_from?: string | null;
  effective_to?: string | null;
  description?: string | null;
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

  listProductVersions(productId: string, signal?: AbortSignal) {
    return request<ProductVersionItemFromAPI[]>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/versions`,
      { signal },
    );
  },

  getProductVersion(productId: string, versionId: string, signal?: AbortSignal) {
    return request<ProductVersionItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/versions/${encodeURIComponent(versionId)}`,
      { signal },
    );
  },
};
