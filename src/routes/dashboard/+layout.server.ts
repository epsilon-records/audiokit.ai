import type { LayoutServerLoad } from './$types';
import { requireAuth, hasActiveSubscription } from '$lib/server/auth';

export const load: LayoutServerLoad = async ({ locals, depends }) => {
  const { auth } = await requireAuth(locals);
  const hasActiveSubscription = await hasActiveSubscription(auth.email);

  return {
    hasActiveSubscription,
  };
};
