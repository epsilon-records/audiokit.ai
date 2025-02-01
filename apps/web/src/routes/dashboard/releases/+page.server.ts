import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { requireAuth } from '$lib/server/auth';
import { error } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

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
