export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface HttpContext {
  authToken?: string | null;
  tenantId?: string | null;
}

export interface RequestOptions {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
}

export class HttpError extends Error {
  status: number;
  detail?: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "HttpError";
    this.status = status;
    this.detail = detail;
  }
}

const API_PREFIX = "/api";

let getHttpContext: (() => HttpContext) | null = null;
let onUnauthorized: (() => void) | null = null;

export const setHttpContextProvider = (provider: () => HttpContext) => {
  getHttpContext = provider;
};

export const setUnauthorizedHandler = (handler: () => void) => {
  onUnauthorized = handler;
};

const normalizePath = (path: string) => {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  if (path.startsWith(API_PREFIX)) {
    return path;
  }

  return `${API_PREFIX}${path.startsWith("/") ? path : `/${path}`}`;
};

const parseResponseBody = async (response: Response): Promise<unknown> => {
  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return response.json().catch(() => null);
  }

  return response.text().catch(() => "");
};

const buildHeaders = (headers?: Record<string, string>, body?: unknown): Headers => {
  const merged = new Headers(headers || {});
  const context = getHttpContext?.() || {};

  if (body !== undefined && !merged.has("Content-Type")) {
    merged.set("Content-Type", "application/json");
  }

  if (context.authToken && !merged.has("Authorization")) {
    merged.set("Authorization", `Bearer ${context.authToken}`);
  }

  if (context.tenantId && !merged.has("X-Tenant-ID")) {
    merged.set("X-Tenant-ID", context.tenantId);
  }

  return merged;
};

export const request = async <T>(path: string, options: RequestOptions = {}): Promise<T> => {
  const { method = "GET", headers, body, signal } = options;

  const response = await fetch(normalizePath(path), {
    method,
    headers: buildHeaders(headers, body),
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });

  const parsedBody = await parseResponseBody(response);

  if (!response.ok) {
    const detail =
      typeof parsedBody === "object" && parsedBody !== null && "detail" in parsedBody
        ? (parsedBody as { detail?: unknown }).detail
        : parsedBody;

    if (response.status === 401) {
      onUnauthorized?.();
    }

    throw new HttpError(
      typeof detail === "string" && detail.trim().length > 0
        ? detail
        : `Request failed (${response.status})`,
      response.status,
      detail,
    );
  }

  return parsedBody as T;
};