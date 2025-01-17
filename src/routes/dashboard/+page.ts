import { redirect } from '@sveltejs/kit';
import type { PageLoadEvent } from './$types';

export async function load({ url, fetch }: PageLoadEvent) {
  const sessionId = url.searchParams.get('session_id');

  if (sessionId) {
    try {
      // Verify the checkout session
      const response = await fetch('/api/verify-session', {
        method: 'POST',
        body: JSON.stringify({ sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to verify session');
      }

      // After verification, redirect to clean URL
      throw redirect(303, '/dashboard');
    } catch (error) {
      throw redirect(303, '/pricing?error=payment-verification-failed');
    }
  }

  // Normal dashboard load logic here
  return {
    // ... other dashboard data
  };
}
