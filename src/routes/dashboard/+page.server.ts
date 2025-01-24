import { getOrg, getUser, requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { getArtistStats, getArtistTracks } from '$lib/server/soundcharts';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import { info } from '$lib/utils/logger';

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

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  let stats = null;
  if (artist?.soundchartsId) {
    stats = await getArtistStats(artist.soundchartsId);
  }

  let tracks = null;
  if (artist?.soundchartsId) {
    tracks = await getArtistTracks(artist.soundchartsId);
  }

  info({
    user: {
      ...user,
      emailAddresses: user.emailAddresses?.map((email) => email.emailAddress),
      phoneNumbers: user.phoneNumbers?.map((phone) => phone.phoneNumber),
    },
  });

  return {
    auth,
    user: {
      ...user,
      emailAddresses: user.emailAddresses?.map((email) => email.emailAddress) ?? [],
      phoneNumbers: user.phoneNumbers?.map((phone) => phone.phoneNumber) ?? [],
    },
    org,
    stats,
    tracks,
  };
}) satisfies PageServerLoad;
