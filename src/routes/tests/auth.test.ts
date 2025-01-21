import { test, expect } from '@playwright/test';

test.describe('Authentication Flows', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing session/cookies before each test
    await page.context().clearCookies();
  });

  test('unauthenticated user is redirected to sign-in', async ({ page }) => {
    // Try accessing a protected route
    const response = await page.goto('/dashboard');

    // Should be redirected to sign-in
    expect(response?.url()).toContain('/sign-in');
    expect(response?.status()).toBe(200);
  });
});
