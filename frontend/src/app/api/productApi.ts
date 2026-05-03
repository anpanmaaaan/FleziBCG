import { request } from "./httpClient";

export interface ProductVersionProductCapabilities {
  can_create: boolean;
}

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
  product_version_capabilities: ProductVersionProductCapabilities;
}

export interface ProductVersionAllowedActions {
  can_update: boolean;
  can_release: boolean;
  can_retire: boolean;
  can_create_sibling: boolean;
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
  allowed_actions: ProductVersionAllowedActions;
}

export interface ProductVersionCreateRequest {
  version_code: string;
  version_name?: string;
  effective_from?: string;
  effective_to?: string;
  description?: string;
}

export interface ProductVersionUpdateRequest {
  version_name?: string;
  effective_from?: string;
  effective_to?: string;
  description?: string;
}

export interface BomItemFromAPI {
  bom_id: string;
  tenant_id: string;
  product_id: string;
  bom_code: string;
  bom_name: string;
  lifecycle_status: "DRAFT" | "RELEASED" | "RETIRED";
  effective_from?: string | null;
  effective_to?: string | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BomComponentItemFromAPI {
  bom_item_id: string;
  tenant_id: string;
  bom_id: string;
  component_product_id: string;
  line_no: number;
  quantity: number;
  unit_of_measure: string;
  scrap_factor?: number | null;
  reference_designator?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BomFromAPI extends BomItemFromAPI {
  items: BomComponentItemFromAPI[];
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

  createProductVersion(productId: string, payload: ProductVersionCreateRequest, signal?: AbortSignal) {
    return request<ProductVersionItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/versions`,
      {
        method: "POST",
        body: payload,
        signal,
      },
    );
  },

  updateProductVersion(
    productId: string,
    versionId: string,
    payload: ProductVersionUpdateRequest,
    signal?: AbortSignal,
  ) {
    return request<ProductVersionItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/versions/${encodeURIComponent(versionId)}`,
      {
        method: "PATCH",
        body: payload,
        signal,
      },
    );
  },

  releaseProductVersion(productId: string, versionId: string, signal?: AbortSignal) {
    return request<ProductVersionItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/versions/${encodeURIComponent(versionId)}/release`,
      {
        method: "POST",
        signal,
      },
    );
  },

  retireProductVersion(productId: string, versionId: string, signal?: AbortSignal) {
    return request<ProductVersionItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/versions/${encodeURIComponent(versionId)}/retire`,
      {
        method: "POST",
        signal,
      },
    );
  },

  listProductBoms(productId: string, signal?: AbortSignal) {
    return request<BomItemFromAPI[]>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/boms`,
      { signal },
    );
  },

  getProductBom(productId: string, bomId: string, signal?: AbortSignal) {
    return request<BomFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(productId)}/boms/${encodeURIComponent(bomId)}`,
      { signal },
    );
  },
};
