import { request, setHttpContextProvider } from "../src/app/api/httpClient.ts";

const originalFetch = globalThis.fetch;

try {
  let capturedHeaders = null;

  globalThis.fetch = async (_url, init = {}) => {
    capturedHeaders = new Headers(init.headers || {});
    return {
      ok: true,
      status: 200,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ ok: true }),
      text: async () => "",
    };
  };

  setHttpContextProvider(() => ({
    authToken: "smoke-token",
    tenantId: "default",
  }));

  await request("/v1/ping");

  const auth = capturedHeaders?.get("Authorization");
  if (auth !== "Bearer smoke-token") {
    throw new Error(`Expected Authorization header, got: ${auth ?? "<missing>"}`);
  }

  const tenant = capturedHeaders?.get("X-Tenant-ID");
  if (tenant !== "default") {
    throw new Error(`Expected X-Tenant-ID header, got: ${tenant ?? "<missing>"}`);
  }

  console.log("PASS: httpClient attaches Authorization and tenant headers when token context is present.");
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`FAIL: ${message}`);
  process.exitCode = 1;
} finally {
  globalThis.fetch = originalFetch;
}
