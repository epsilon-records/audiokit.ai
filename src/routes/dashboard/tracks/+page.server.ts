import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { getTrackMetadata } from '$lib/server/integrations/soundcharts';
import logger from '$lib/utils/logger';

interface Artist {
  id: string;
  name: string;
  tracks: Track[];
}

interface Track {
  id: string;
  title: string;
  // Add other track properties as needed
}

export const load: PageServerLoad = async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));
  logger.info({
    artist,
    msg: 'Artist',
  });

  const tracksWithMetadata = await Promise.all(
    (artist?.tracks as { items: any[] })?.items?.map(async (track) => ({
      ...track,
      metadata: await getTrackMetadata(track.uuid),
    })) ?? []
  );

  return {
    auth,
    artist,
    tracks: tracksWithMetadata,
  };
};
