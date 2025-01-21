import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { releases } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);

  try {
    const userReleases = await db.select().from(releases).where(eq(releases.orgId, auth.orgId));

    return {
      auth,
      releases: userReleases,
    };
  } catch (err) {
    throw error(500, 'Error fetching releases');
  }
}) satisfies PageServerLoad;
