import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { invalidateAll } from '$app/navigation';

export const load = (async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  }
}) satisfies PageServerLoad;
