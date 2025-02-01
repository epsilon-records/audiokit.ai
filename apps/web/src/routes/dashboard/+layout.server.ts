import { requireAuth } from '$lib/server/auth';
import type { LayoutServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  return { auth };
}) satisfies LayoutServerLoad;
