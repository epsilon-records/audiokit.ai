import { redirectAuthenticated } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  redirectAuthenticated(locals, 307, '/dashboard');
  return {};
}) satisfies PageServerLoad;
