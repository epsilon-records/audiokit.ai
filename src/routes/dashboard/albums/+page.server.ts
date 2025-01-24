import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { getArtistAlbums } from '$lib/server/soundcharts';
import { info } from '$lib/utils/logger';

export const load: PageServerLoad = async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  let albums = [];
  if (artist?.soundchartsId) {
    const albumsData = await getArtistAlbums(artist.soundchartsId);
    info({
      msg: 'Albums data',
      data: albumsData,
    });
    albums = albumsData?.items || [];
  }

  return {
    auth,
    albums,
  };
};
