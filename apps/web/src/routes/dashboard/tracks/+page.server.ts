/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { requireAuth } from '$lib/server/auth';
import { getTrackMetadata } from '$lib/server/integrations/soundcharts';
import logger from '$lib/utils/logger';
import { error } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

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
  logger.data(crypto.randomUUID(), 'Retrieved artist', artist);

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
