import type { PageServerLoad } from './$types';
import { requireSubscription } from '$lib/server/auth';

export const load = (async ({ locals }) => {
  const auth = await requireSubscription(locals);
  return { auth };
}) satisfies PageServerLoad;
