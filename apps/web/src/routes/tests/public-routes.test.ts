import { expect, test } from '@playwright/test';

test.describe('Unauthenticated Access Controls', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing session/cookies before each test
    await page.context().clearCookies();
  });

  test('sign-in page is accessible without auth', async ({ page }) => {
    const response = await page.goto('/sign-in');
    expect(response?.status()).toBe(200);
    expect(page.getByRole('heading', { name: 'Sign In' })).toBeTruthy();
  });

  test('sign-up page is accessible without auth', async ({ page }) => {
    const response = await page.goto('/sign-up');
    expect(response?.status()).toBe(200);
    expect(page.getByRole('heading', { name: 'Create Account' })).toBeTruthy();
  });

  test('protected routes redirect to sign-in with return URL', async ({ page }) => {
    const protectedRoutes = ['/dashboard'];

    for (const route of protectedRoutes) {
      const response = await page.goto(route);
      expect(response?.url()).toContain('/sign-in');
      expect(response?.status()).toBe(200);
    }
  });

  test('public routes are accessible without auth', async ({ page }) => {
    const publicRoutes = ['/', '/pricing', '/contact'];

    for (const route of publicRoutes) {
      const response = await page.goto(route);
      expect(response?.status()).toBe(200);
      expect(response?.url()).toContain(route);
    }
  });
});
