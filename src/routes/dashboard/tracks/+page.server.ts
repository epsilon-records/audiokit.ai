import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { getArtistTracks, getTrackMetadata } from '$lib/server/soundcharts';
import { info, debug } from '$lib/utils/logger';
import type { Track } from '$lib/types/track';

export const load: PageServerLoad = async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  let tracks: Track[] = [];
  if (artist?.soundchartsId) {
    const tracksData = await getArtistTracks(artist.soundchartsId);
    debug({
      msg: 'Tracks data',
      data: tracksData,
    });

    const trackPromises = (tracksData?.items || []).map(async (track) => {
      const trackData = await getTrackMetadata(track.uuid);
      debug({
        msg: 'Track data',
        data: trackData,
      });
      return {
        ...track,
        ...trackData,
      } as Track;
    });

    tracks = await Promise.all(trackPromises);
  }

  return {
    auth,
    tracks: tracks || [],
  };
};
