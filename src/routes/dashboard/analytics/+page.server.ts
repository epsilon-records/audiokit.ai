import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);

  return {
    auth,
    streaming: null,
    social: null,
    revenue: null,
    dateRange: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      end: new Date(),
    },
  };
}) satisfies PageServerLoad;
