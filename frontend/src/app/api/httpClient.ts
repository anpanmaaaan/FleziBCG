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
  /** Internal: set to true when retrying after a successful token refresh. Do not set externally. */
  retried?: boolean;
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

const isDevAuthDebugEnabled = () => {
  return Boolean(import.meta.env?.DEV && import.meta.env?.VITE_HTTP_DEBUG_AUTH === "1");
};

// Paths that must never trigger a refresh-and-retry cycle.
// Login 401 = bad credentials (propagate to caller).
// Refresh 401 = refresh token expired/revoked (clearLocalAuthState is called inside refreshHandler).
// Logout 401 = best-effort; local state is cleared regardless.
const REFRESH_EXCLUDED_PATHS = [
  "/v1/auth/login",
  "/v1/auth/refresh",
  "/v1/auth/logout",
  "/v1/auth/logout-all",
];

function isExcludedFromRefresh(path: string): boolean {
  const n = normalizePath(path);
  return REFRESH_EXCLUDED_PATHS.some((excluded) => n.endsWith(excluded));
}

let getHttpContext: (() => HttpContext) | null = null;
let onUnauthorized: (() => void) | null = null;
let refreshHandler: (() => Promise<boolean>) | null = null;
// Shared in-flight refresh promise: parallel 401s await the same refresh instead of each
// spawning a separate rotation (which would invalidate each other under token rotation).
let refreshInFlight: Promise<boolean> | null = null;

export const setHttpContextProvider = (provider: () => HttpContext) => {
  getHttpContext = provider;
};

export const setUnauthorizedHandler = (handler: () => void) => {
  onUnauthorized = handler;
};

/**
 * Register the refresh handler used to rotate the access/refresh token pair after a 401.
 * The handler must return true if rotation succeeded and false (or throw) if it failed.
 * Called by AuthContext — do not call from application code.
 */
export const setRefreshHandler = (handler: () => Promise<boolean>) => {
  refreshHandler = handler;
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
  const requestHeaders = buildHeaders(headers, body);

  if (isDevAuthDebugEnabled()) {
    const hasAuth = requestHeaders.has("Authorization");
    const normalized = normalizePath(path);
    if (hasAuth) {
      console.debug(`[httpClient] Authorization attached: ${method} ${normalized}`);
    } else {
      console.debug(`[httpClient] No Authorization header: ${method} ${normalized}`);
    }
  }

  const response = await fetch(normalizePath(path), {
    method,
    headers: requestHeaders,
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
      if (!options.retried && !isExcludedFromRefresh(path) && refreshHandler) {
        // Attempt token rotation. Deduplicate so parallel 401s share one refresh call.
        if (!refreshInFlight) {
          refreshInFlight = refreshHandler().finally(() => {
            refreshInFlight = null;
          });
        }
        let refreshed = false;
        try {
          refreshed = await refreshInFlight;
        } catch {
          refreshed = false;
        }
        if (refreshed) {
          // Retry original request exactly once. buildHeaders will pick up the new
          // access token that AuthContext already placed into getHttpContext.
          return request<T>(path, { ...options, retried: true });
        }
        // Refresh failed — AuthContext.refreshTokens() already called clearLocalAuthState.
        // Fall through to throw.
      } else {
        // Non-retryable 401 (excluded endpoint, already retried, or no handler).
        onUnauthorized?.();
      }
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