import { redirect } from '@sveltejs/kit';
import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  requireAuth(locals);
  return {};
}) satisfies PageServerLoad;
