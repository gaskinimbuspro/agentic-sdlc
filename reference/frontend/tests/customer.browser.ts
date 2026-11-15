import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function fillCustomer(page: Page, name: string, email: string) {
  await page.getByLabel("Name").fill(name);
  await page.getByLabel("Email").fill(email);
}

test("lists only the tenant, with keyboard navigation and automated accessibility checks", async ({
  page,
}, info) => {
  await page.goto("/customers");
  await expect(page.getByText("Current tenant fixture")).toBeVisible();
  await expect(page.getByText("Other tenant fixture")).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "Customers" })).toBeFocused();
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.screenshot({ path: info.outputPath("customer-list.png") });

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Add customer" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("heading", { name: "Add customer" }),
  ).toBeFocused();
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.setViewportSize({ width: 360, height: 800 });
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(360);
  await page.screenshot({ path: info.outputPath("customer-form-360.png") });
  await page.goBack();
  await expect(page.getByRole("heading", { name: "Customers" })).toBeFocused();
});

test("creates through the real API and presents a real duplicate error", async ({
  page,
}, info) => {
  const email = "pilot-" + info.project.name + "@example.test";
  await page.goto("/customers/new");
  await page.reload();
  await fillCustomer(page, "Pilot customer", email);
  await page.getByRole("button", { name: "Save customer" }).click();
  await expect(
    page
      .getByRole("status")
      .filter({ hasText: "Saved customer Pilot customer" }),
  ).toBeVisible();
  await expect(page.getByRole("cell", { name: email })).toBeVisible();

  await page.getByRole("link", { name: "Add customer" }).click();
  await fillCustomer(page, "Duplicate name", email);
  await page.getByRole("button", { name: "Save customer" }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "A customer with this email already exists.",
  );
  await expect(page.getByRole("alert")).toBeFocused();
  await expect(page.getByLabel("Email")).toHaveValue(email);
});

test("cancels without sending a create request", async ({ page }) => {
  const creates: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST") creates.push(request.url());
  });
  await page.goto("/customers/new");
  await fillCustomer(page, "Cancelled", "cancelled@example.test");
  await page.getByRole("link", { name: "Cancel" }).click();
  await expect(page.getByText("Current tenant fixture")).toBeVisible();
  await expect(page.getByText("cancelled@example.test")).toHaveCount(0);
  expect(creates).toEqual([]);
});

test("blocks a second create when the transport fails after the real write", async ({
  page,
}, info) => {
  const email = "uncertain-" + info.project.name + "@example.test";
  let writes = 0;
  let upstreamStatus = 0;
  await page.route("**/api/customers", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    writes++;
    const result = await route.fetch();
    upstreamStatus = result.status();
    await route.fulfill({ status: 503, body: "" });
  });
  await page.goto("/customers");
  await page.getByRole("link", { name: "Add customer" }).click();
  await fillCustomer(page, "Uncertain customer", email);
  await page.getByRole("button", { name: "Save customer" }).click();
  await expect(page.getByRole("alert")).toContainText("could not confirm");
  await expect(page.getByRole("button", { name: "Save customer" })).toHaveCount(
    0,
  );
  await page.reload();
  await expect(page.getByRole("alert")).toContainText("could not confirm");
  await page.goBack();
  await expect(page.getByRole("heading", { name: "Customers" })).toBeVisible();
  await page.goForward();
  await expect(page.getByRole("alert")).toContainText("could not confirm");
  await expect(page.getByRole("button", { name: "Save customer" })).toHaveCount(
    0,
  );
  await page.getByRole("link", { name: "Back to customers" }).click();
  await expect(page.getByRole("cell", { name: email })).toBeVisible();
  expect(upstreamStatus).toBe(201);
  expect(writes).toBe(1);
});

test("recovers after a list connection failure", async ({ page }) => {
  let reads = 0;
  await page.route("**/api/customers", (route) => {
    reads++;
    return reads === 1 ? route.abort() : route.continue();
  });
  await page.goto("/customers");
  await expect(page.getByRole("alert")).toHaveText(
    "We could not load customers.",
  );
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByText("Current tenant fixture")).toBeVisible();
  expect(reads).toBe(2);
});
