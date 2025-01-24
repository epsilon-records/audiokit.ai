import { getOrg, getUser, requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { getArtistStats } from '$lib/server/soundcharts';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const user = await getUser(auth.userId);
  if (!user) {
    throw error(404, 'User not found');
  }

  const org = await getOrg(auth.orgId);
  if (!org) {
    throw error(404, 'Organization not found');
  }

  // Get artist record to find soundchartsId
  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  let stats = null;
  if (artist?.soundchartsId) {
    stats = await getArtistStats(artist.soundchartsId);
  }

  return {
    auth,
    user,
    org,
    stats,
  };
}) satisfies PageServerLoad;
