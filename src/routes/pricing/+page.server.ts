import type { PageServerLoad } from './$types';
import { redirectAuthenticated } from '$lib/server/auth';

export const load = (async ({ locals }) => {
  redirectAuthenticated(locals, 303, '/join');

  return {
    title: 'Simple, Transparent Pricing',
    description: 'Choose the perfect plan for your needs with our straightforward pricing options.',
  };
}) satisfies PageServerLoad;
