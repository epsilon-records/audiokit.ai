import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);

  return {
    auth,
    title: 'Get Started with AudioKit',
    description: 'Choose the perfect plan for your needs with our straightforward pricing options.',
  };
}) satisfies PageServerLoad;
