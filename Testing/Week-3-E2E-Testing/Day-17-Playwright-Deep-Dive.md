# Day 17: Playwright Deep Dive – Cross-Browser E2E Testing

## 📚 Topics to Cover (3-4 hours)

---

## 1. Why Playwright?

| Feature | Playwright | Cypress | Selenium |
|---------|-----------|---------|----------|
| Browsers | Chromium, Firefox, WebKit | Chromium, Firefox, Edge | All browsers |
| Speed | Very Fast | Fast | Slow |
| Auto-wait | ✅ Built-in | ✅ Built-in | ❌ Manual |
| Multi-tab | ✅ Yes | ❌ No | ✅ Yes |
| iFrames | ✅ Easy | ⚠️ Limited | ✅ Yes |
| Network Mock | ✅ Yes | ✅ Yes | ❌ No |
| Parallel | ✅ Built-in | ⚠️ Plugin | ✅ Grid |
| Language | JS/TS/Python/C#/Java | JS/TS only | All |
| Mobile | ✅ Emulation | ❌ Limited | ✅ Appium |

---

## 2. Setup

```bash
npm init playwright@latest
# or
npm install -D @playwright/test
npx playwright install  # Download browsers
```

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'results.json' }],
    process.env.CI ? ['github'] : ['list'],
  ],
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:4200',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 3. Core API

```typescript
import { test, expect } from '@playwright/test';

test('basic navigation', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/My App/);
  await expect(page).toHaveURL('/');
});

// Locators (recommended)
const submitBtn = page.getByRole('button', { name: 'Submit' });
const emailInput = page.getByLabel('Email');
const heading = page.getByRole('heading', { level: 1 });
const item = page.getByText('Item 1');
const testId = page.getByTestId('search-input');
const placeholder = page.getByPlaceholder('Search...');

// Actions
await emailInput.fill('user@test.com');
await submitBtn.click();
await page.getByRole('checkbox').check();
await page.getByRole('combobox').selectOption('Option 1');
await page.keyboard.press('Enter');
await page.mouse.click(100, 200);

// Assertions (auto-retry)
await expect(submitBtn).toBeVisible();
await expect(submitBtn).toBeEnabled();
await expect(emailInput).toHaveValue('user@test.com');
await expect(page.getByRole('alert')).toHaveText('Success!');
await expect(page.getByRole('listitem')).toHaveCount(5);
await expect(submitBtn).toHaveClass(/primary/);
await expect(page).toHaveURL('/dashboard');
```

---

## 4. Test Patterns

### Authentication with Storage State

```typescript
// auth.setup.ts - Run once, save session
import { test as setup } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@test.com');
  await page.getByLabel('Password').fill('Admin123!');
  await page.getByRole('button', { name: 'Log in' }).click();
  await page.waitForURL('/dashboard');

  // Save authentication state
  await page.context().storageState({ path: '.auth/user.json' });
});

// Use in tests
test.use({ storageState: '.auth/user.json' });

test('should access dashboard', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByText('Welcome')).toBeVisible();
});
```

### API Mocking

```typescript
test('should display users from API', async ({ page }) => {
  // Mock API
  await page.route('/api/users', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'John' },
        { id: 2, name: 'Jane' },
      ]),
    });
  });

  await page.goto('/users');
  await expect(page.getByRole('listitem')).toHaveCount(2);
});

// Mock error
await page.route('/api/users', (route) => {
  route.fulfill({ status: 500 });
});

// Modify real response
await page.route('/api/users', async (route) => {
  const response = await route.fetch();
  const json = await response.json();
  json.push({ id: 999, name: 'Injected User' });
  await route.fulfill({ response, json });
});

// Abort request
await page.route('**/*.{png,jpg}', (route) => route.abort());
```

---

## 5. Advanced Features

### Multi-tab/Multi-window

```typescript
test('should open in new tab', async ({ page, context }) => {
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.getByText('Open in new tab').click(),
  ]);
  await newPage.waitForLoadState();
  await expect(newPage).toHaveURL('/new-page');
});
```

### File Upload/Download

```typescript
// Upload
test('should upload file', async ({ page }) => {
  await page.getByLabel('Upload').setInputFiles('test-data/photo.jpg');
  // Multiple files
  await page.getByLabel('Upload').setInputFiles(['file1.pdf', 'file2.pdf']);
});

// Download
test('should download report', async ({ page }) => {
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByText('Download Report').click(),
  ]);
  const path = await download.path();
  expect(download.suggestedFilename()).toBe('report.pdf');
});
```

### Visual Comparison

```typescript
test('visual regression', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 100,
  });

  // Element screenshot
  await expect(page.getByTestId('chart')).toHaveScreenshot('chart.png');
});
```

### Trace Viewer

```bash
# Record trace
npx playwright test --trace on

# View trace
npx playwright show-trace trace.zip
```

---

## 6. Page Object Model in Playwright

```typescript
// pages/LoginPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Log in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}

// Test
test('login flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@test.com', 'password');
  await expect(page).toHaveURL('/dashboard');
});
```

---

## 🎯 Interview Questions

### Q1: When would you choose Playwright over Cypress?
**A:** Choose Playwright for cross-browser testing (Safari via WebKit), multi-tab scenarios, iFrame testing, mobile emulation, non-JS languages (Python/C#), or when you need parallel execution out of the box. Cypress is simpler for single-browser, component-level testing.

### Q2: How does Playwright's auto-wait work?
**A:** Playwright auto-waits for elements to be actionable before performing actions. For click: waits for visible, stable, enabled, receives events. For fill: waits for visible, enabled, editable. Assertions retry until timeout. This eliminates flaky tests from race conditions.

### Q3: How do you handle authentication in Playwright tests?
**A:** Use `storageState` to save and reuse authentication. Run a setup project that logs in once and saves cookies/localStorage to a file. Other tests load this state, avoiding login in every test. This is faster and more reliable than repeating login flows.

---

## 📝 Practice Exercises

1. Write cross-browser E2E tests for a shopping cart
2. Implement API mocking for loading, success, and error states
3. Create Page Objects for a multi-page application
4. Set up visual regression tests with screenshot comparison
