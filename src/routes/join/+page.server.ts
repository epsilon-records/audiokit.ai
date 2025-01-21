import type { PageServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);

  return {
    auth,
    title: 'Get Started with AudioKit',
    description:
      'Choose the perfect plan for your music distribution needs with our straightforward pricing options.',
  };
}) satisfies PageServerLoad;
