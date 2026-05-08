import { expect, test } from "@playwright/test";

const MOCK_USER = {
  user_id: "user-qm-01",
  username: "quality_user",
  email: "quality@test.local",
  tenant_id: "tenant-quality-01",
  role_code: "QAL",
  session_id: "session-qm-01",
};

const REQUIREMENTS_RESPONSE = {
  operation_id: 101,
  operation_number: "OP-0101",
  operation_name: "Quality Check",
  qc_required: true,
  template_code: "QLITE-STD-001",
  template_name: "Quality Lite Baseline Inspection",
  template_version: "v1",
  items: [
    {
      item_code: "DIM_A",
      label: "Dimension A",
      input_type: "number",
      required: true,
      unit: "mm",
      lower_limit: 10.0,
      upper_limit: 10.5,
    },
    {
      item_code: "DIM_B",
      label: "Dimension B",
      input_type: "number",
      required: true,
      unit: "mm",
      lower_limit: 5.0,
      upper_limit: 5.5,
    },
    {
      item_code: "SURF",
      label: "Surface Variation",
      input_type: "number",
      required: true,
      unit: null,
      lower_limit: null,
      upper_limit: 2.0,
    },
  ],
};

async function seedAuthState(page: import("@playwright/test").Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem("mes.auth.token", "quality-access-token");
    window.localStorage.setItem("mes.auth.refresh_token", "quality-refresh-token");
  });
}

test("quality measurement submit remains disabled until all required rows are filled", async ({ page }) => {
  let submitRequestBody: unknown = null;

  await seedAuthState(page);

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

  await page.route("**/api/v1/quality/operations/101/requirements", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(REQUIREMENTS_RESPONSE),
    });
  });

  await page.route("**/api/v1/quality/measurements", async (route, request) => {
    submitRequestBody = await request.postDataJSON();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        measurement_record_id: 9001,
        operation_id: 101,
        quality_status: "QC_PASSED",
        review_status: "NO_REVIEW",
        accepted_good_release_qty: 3,
        held_pending_good_qty: 0,
        hold_id: null,
        submitted_at: "2026-05-08T09:00:00Z",
        values: [
          {
            item_code: "DIM_A",
            measured_value: 10.1,
            lower_limit: 10.0,
            upper_limit: 10.5,
            is_within_spec: true,
          },
          {
            item_code: "DIM_B",
            measured_value: 5.2,
            lower_limit: 5.0,
            upper_limit: 5.5,
            is_within_spec: true,
          },
          {
            item_code: "SURF",
            measured_value: 1.0,
            lower_limit: null,
            upper_limit: 2.0,
            is_within_spec: true,
          },
        ],
      }),
    });
  });

  await page.goto("/quality-measurements");

  await page.getByLabel("Operation ID").fill("101");
  await page.getByRole("button", { name: "Load Requirements" }).click();

  const submitButton = page.getByRole("button", { name: "Submit Measurement" });
  await expect(submitButton).toBeDisabled();

  await page.getByPlaceholder("Measured value").first().fill("10.1");
  await expect(submitButton).toBeDisabled();

  const measuredInputs = page.getByPlaceholder("Measured value");
  await measuredInputs.nth(1).fill("5.2");
  await expect(submitButton).toBeDisabled();

  await measuredInputs.nth(2).fill("1.0");
  await expect(submitButton).toBeEnabled();

  await submitButton.click();

  await expect(page.getByText("Measurement Recorded")).toBeVisible();

  expect(submitRequestBody).toEqual({
    operation_id: 101,
    measurements: [
      { item_code: "DIM_A", measured_value: 10.1 },
      { item_code: "DIM_B", measured_value: 5.2 },
      { item_code: "SURF", measured_value: 1.0 },
    ],
  });
});
