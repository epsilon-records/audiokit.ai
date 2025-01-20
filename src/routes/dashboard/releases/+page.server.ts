import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  } else if (!locals.auth.orgId) {
    throw redirect(307, '/dashboard/create-artist');
  }
  const releases = null;
  return { releases: releases };
}) satisfies PageServerLoad;
