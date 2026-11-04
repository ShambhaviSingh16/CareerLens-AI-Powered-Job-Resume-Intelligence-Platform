import { test, expect } from "@playwright/test";

test("landing explains the product and links to a usable example", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Your experience/ })).toBeVisible();
  if (process.env.CAPTURE_DOCS && testInfo.project.name === "desktop") await page.screenshot({ path: "../docs/screenshots/landing.png", fullPage: true });
  await page.getByRole("button", { name: "Show example 3" }).click();
  await expect(page.locator(".annotation h4")).toHaveText("Automated testing");
  await page.getByRole("link", { name: "Take a look inside" }).click();
  await expect(page.locator(".sample-stamp")).toContainText("FICTIONAL DATA");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
});

test("report filters, keyboard tabs, and export work", async ({ page }, testInfo) => {
  await page.goto("/sample");
  if (process.env.CAPTURE_DOCS && testInfo.project.name === "desktop") await page.screenshot({ path: "../docs/screenshots/report.png", fullPage: true });
  await page.getByRole("button", { name: /Missing/ }).click();
  await expect(page.locator(".skill-row")).toHaveCount(1);
  await expect(page.locator(".skill-row h3")).toHaveText("Automated testing");
  await page.getByRole("tab", { name: /Skill evidence/ }).focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator(".edit-rewrite")).toBeVisible();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator(".document-check")).toHaveCount(4);
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: /Download report/ }).click();
  expect((await downloadEvent).suggestedFilename()).toBe("careerlens-report.json");
});

test("real account lifecycle and protected workspace", async ({ page }, testInfo) => {
  const email = "browser-" + Date.now() + "-" + Math.random().toString(16).slice(2) + "@example.com";
  const password = "Browser-test-password-123";
  let token;
  let deleted = false;
  const api = process.env.PLAYWRIGHT_API_URL || (process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:8080") + "/api";
  try {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login$/);
    await page.getByRole("link", { name: /Create an account/ }).click();
    await page.getByLabel("Email address").fill(email);
    await page.getByLabel("Password", { exact: true }).fill(password);
    const registration = page.waitForResponse(response => response.url().endsWith("/auth/register") && response.request().method() === "POST");
    await page.getByRole("button", { name: "Create my account" }).click();
    expect((await registration).status()).toBe(201);
    await expect(page.getByRole("status")).toContainText("Your account is ready");
    await page.getByLabel("Email address").fill(email);
    await page.getByLabel("Password", { exact: true }).fill(password);
    await page.getByRole("button", { name: "Enter my workspace" }).click();
    await expect(page.locator(".analysis-form")).toBeVisible();
    token = await page.evaluate(() => sessionStorage.getItem("token"));
    if (process.env.CAPTURE_DOCS && testInfo.project.name === "desktop") {
      await expect(page.locator(".workspace-history")).not.toContainText("Loading your reports");
      await page.screenshot({ path: "../docs/screenshots/workspace.png", fullPage: true });
    }
    await page.getByLabel(/Job title/).fill("Backend developer");
    await page.getByLabel(/Job description/).fill("Build Python APIs and write automated tests. Work with PostgreSQL and collaborate on backend services.");
    await expect(page.locator(".character-count")).not.toContainText("0 / 12,000");
    await page.getByRole("button", { name: /New analysis/ }).click();
    await expect(page.getByLabel(/Job title/)).toHaveValue("");
    await page.getByRole("link", { name: "Account & data" }).click();
    await page.getByLabel("Confirm your password").fill(password);
    await page.getByRole("checkbox").check();
    await page.getByRole("button", { name: "Permanently delete my account" }).click();
    await expect(page).toHaveURL(/\/$/);
    const response = await page.request.get(api + "/auth/me", { headers: { Authorization: "Bearer " + token } });
    expect(response.status()).toBe(401);
    token = null;
    deleted = true;
  } finally {
    if (!deleted && !token) {
      const login = await page.request.post(api + "/auth/login", { data: { email, password } });
      if (login.ok()) token = (await login.json()).access_token;
    }
    if (token) await page.request.delete(api + "/auth/me", { headers: { Authorization: "Bearer " + token }, data: { password } });
  }
});
