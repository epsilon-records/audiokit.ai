import { redirectAuthenticated } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  redirectAuthenticated(locals, 303, '/upgrade');

  return {
    title: 'Simple, Transparent Pricing',
    description: 'Choose the perfect plan for your needs with our straightforward pricing options.',
  };
}) satisfies PageServerLoad;
