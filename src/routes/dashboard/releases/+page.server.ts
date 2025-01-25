import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { releases, artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  return {
    auth,
    artist,
  };
};
