import type { LayoutServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  return { auth };
}) satisfies LayoutServerLoad;
