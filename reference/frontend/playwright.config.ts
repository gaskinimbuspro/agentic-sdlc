import { defineConfig, devices } from "@playwright/test";

const port = process.env.REFERENCE_UI_PORT ?? "4173";
if (!/^\d{1,5}$/.test(port)) throw new Error("Invalid preview port");
const baseURL = "http://127.0.0.1:" + port;

export default defineConfig({
  testDir: "tests",
  testMatch: "*.browser.ts",
  outputDir: "test-results/browser",
  workers: 1,
  retries: 0,
  forbidOnly: true,
  timeout: 30_000,
  reporter: [["list"], ["junit", { outputFile: "test-results/browser.xml" }]],
  use: { baseURL, trace: "retain-on-failure", screenshot: "only-on-failure" },
  webServer: {
    command: "npm run preview -- --port " + port,
    url: baseURL + "/customers",
    timeout: 20_000,
    reuseExistingServer: false,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
});
