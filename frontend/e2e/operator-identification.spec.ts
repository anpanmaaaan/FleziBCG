import { expect, test } from "@playwright/test";

const MOCK_USER = {
  user_id: "opr-e2e-01",
  username: "operator_e2e",
  email: "operator@test.local",
  tenant_id: "tenant-01",
  role_code: "OPR",
  session_id: "session-auth-01",
};

async function seedAuthState(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("mes.auth.token", "station-access-token");
    window.localStorage.setItem("mes.auth.refresh_token", "station-refresh-token");
  });
}

async function mockAuth(page: import("@playwright/test").Page) {
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_USER),
    });
  });

  await page.route("**/api/v1/impersonations/current", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: "null",
    });
  });
}

test("operator identification resolves active session and identifies operator", async ({ page }) => {
  await seedAuthState(page);
  await mockAuth(page);

  let identifyRequestBody: Record<string, unknown> | null = null;

  await page.route("**/api/v1/station/sessions/current?station_id=ST-01", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session: {
          session_id: "sess-001",
          tenant_id: "tenant-01",
          station_id: "ST-01",
          operator_user_id: null,
          equipment_id: null,
          status: "OPEN",
          opened_at: "2026-05-08T08:00:00Z",
          closed_at: null,
        },
      }),
    });
  });

  await page.route("**/api/v1/station/sessions/sess-001/identify-operator", async (route, request) => {
    identifyRequestBody = (await request.postDataJSON()) as Record<string, unknown>;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session_id: "sess-001",
        tenant_id: "tenant-01",
        station_id: "ST-01",
        operator_user_id: "OPR-9001",
        equipment_id: null,
        status: "OPEN",
        opened_at: "2026-05-08T08:00:00Z",
        closed_at: null,
      }),
    });
  });

  await page.goto("/operator-identification?stationId=ST-01&sessionId=sess-001&operationId=17");

  await expect(page.getByRole("heading", { name: "Operator Identification" })).toBeVisible();
  await expect(page.getByText("sess-001")).toBeVisible();

  const operatorInput = page.getByLabel("Operator ID input");
  await operatorInput.fill("OPR-9001");
  await page.getByRole("button", { name: "Identify Operator" }).first().click();

  expect(identifyRequestBody).not.toBeNull();
  expect(identifyRequestBody?.operator_user_id).toBe("OPR-9001");

  await expect(page.locator("*:visible", { hasText: "Verified" }).first()).toBeVisible();
  await expect(page.locator("*:visible", { hasText: "Operator identified as OPR-9001." }).first()).toBeVisible();
});

test("operator identification shows backend rejection state", async ({ page }) => {
  await seedAuthState(page);
  await mockAuth(page);

  await page.route("**/api/v1/station/sessions/current?station_id=ST-02", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        session: {
          session_id: "sess-002",
          tenant_id: "tenant-01",
          station_id: "ST-02",
          operator_user_id: null,
          equipment_id: null,
          status: "OPEN",
          opened_at: "2026-05-08T09:00:00Z",
          closed_at: null,
        },
      }),
    });
  });

  await page.route("**/api/v1/station/sessions/sess-002/identify-operator", async (route) => {
    await route.fulfill({
      status: 403,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Station is outside your station scope" }),
    });
  });

  await page.goto("/operator-identification?stationId=ST-02&sessionId=sess-002");

  const operatorInput = page.getByLabel("Operator ID input");
  await operatorInput.fill("OPR-0002");
  await page.getByRole("button", { name: "Identify Operator" }).first().click();

  await expect(
    page.locator("*:visible", { hasText: "Unable to identify operator with current station session context." }).first()
  ).toBeVisible();
});
