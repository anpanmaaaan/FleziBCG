import { expect, test } from "@playwright/test";

const ACCESS_TOKEN_KEY = "mes.auth.token";
const REFRESH_TOKEN_KEY = "mes.auth.refresh_token";

const MOCK_USER = {
  user_id: "user-header-01",
  username: "header_user",
  email: "header@test.local",
  tenant_id: "tenant-header-01",
  role_code: "PMG",
  session_id: "session-header-01",
};

async function seedAuthState(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("mes.auth.token", "header-access-token");
    window.localStorage.setItem("mes.auth.refresh_token", "header-refresh-token");
  });
}

async function mockShellApis(page: import("@playwright/test").Page) {
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

test("desktop operational header renders with safe context and route disclosure", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await seedAuthState(page);
  await mockShellApis(page);

  await page.goto("/integration");

  await expect(page.getByRole("button", { name: "Open user menu" })).toBeVisible();
  await expect(page.getByText("tenant-header-01").first()).toBeVisible();
  await expect(page.getByText("Context pending").first()).toBeVisible();

  await expect(page.getByText("Not Implemented").first()).toBeVisible();

  const storedAccess = await page.evaluate((key) => window.localStorage.getItem(key), ACCESS_TOKEN_KEY);
  const storedRefresh = await page.evaluate((key) => window.localStorage.getItem(key), REFRESH_TOKEN_KEY);
  expect(storedAccess).toBe("header-access-token");
  expect(storedRefresh).toBe("header-refresh-token");
});

test("mobile drawer opens and returns focus to menu button", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await seedAuthState(page);
  await mockShellApis(page);

  await page.goto("/integration");

  const menuButton = page.getByRole("button", { name: "Open navigation drawer" });
  await expect(menuButton).toBeVisible();

  await menuButton.click();
  await expect(page.getByRole("dialog")).toBeVisible();

  const closeButton = page.locator('#app-mobile-navigation-drawer button[aria-label="Close navigation drawer"]');
  await closeButton.click();

  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(menuButton).toBeFocused();
});
