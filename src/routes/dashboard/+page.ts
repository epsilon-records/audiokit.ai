import { redirect } from '@sveltejs/kit';
import type { PageLoadEvent } from './$types';

export async function load({ url, fetch }: PageLoadEvent) {
  const sessionId = url.searchParams.get('session_id');
  if (sessionId) {
    const response = await fetch('/api/verify-session', {
      method: 'POST',
      body: JSON.stringify({ sessionId }),
    }).catch(() => {
      throw redirect(303, '/subscribe?error=payment-verification-failed');
    });

    if (!response.ok) {
      throw redirect(303, '/subscribe?error=payment-verification-failed');
    }
    throw redirect(303, '/dashboard');
  }
}
