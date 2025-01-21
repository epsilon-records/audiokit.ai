import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  return { auth };
}) satisfies PageServerLoad;
