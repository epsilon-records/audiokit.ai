import type { PageServerLoad } from './$types';
import { redirectUnauthenticated } from '$lib/server/auth';

export const load = (async ({ locals }) => {
  redirectUnauthenticated(locals, 307, '/sign-in');
  return {};
}) satisfies PageServerLoad;
