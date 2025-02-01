import { redirectUnauthenticated } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  redirectUnauthenticated(locals, 307, '/sign-in');
  return {};
}) satisfies PageServerLoad;
