import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import { getArtistIdFromSpotify, getArtistStats, getArtistTracks } from '../soundcharts.js';
import { eq } from 'drizzle-orm';
import { debug, warn } from '../../utils/logger.js';
import { error } from '@sveltejs/kit';

function extractSpotifyId(spotifyUrl: string): string | null {
  try {
    const id = spotifyUrl.split('/').pop();
    return id || null;
  } catch {
    return null;
  }
}

async function updateArtist(artist: typeof artists.$inferSelect) {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      artistId: artist.id,
      msg: 'Starting artist update process',
    });

    let soundchartsId = artist.soundchartsId;
    debug({
      requestId,
      artistId: artist.id,
      soundchartsId,
      msg: 'Initial soundchartsId status',
    });

    if (!soundchartsId && artist.spotify) {
      debug({
        requestId,
        artistId: artist.id,
        spotifyUrl: artist.spotify,
        msg: 'Attempting to get soundchartsId from Spotify URL',
      });

      const spotifyId = extractSpotifyId(artist.spotify);
      if (spotifyId) {
        soundchartsId = await getArtistIdFromSpotify(spotifyId);

        if (soundchartsId) {
          debug({
            requestId,
            artistId: artist.id,
            soundchartsId,
            msg: 'Retrieved and updating new soundchartsId',
          });

          await db.update(artists).set({ soundchartsId }).where(eq(artists.id, artist.id));
        }
      }
    }

    if (!soundchartsId) {
      warn({
        requestId,
        artistId: artist.id,
        msg: 'No Soundcharts ID available',
      });
      return {
        artistId: artist.id,
        success: false,
        error: 'No Soundcharts ID available',
      };
    }

    debug({
      requestId,
      artistId: artist.id,
      soundchartsId,
      msg: 'Fetching Soundcharts stats',
    });

    const {
      metadata = {},
      streaming = {},
      followers = {},
    } = (await getArtistStats(soundchartsId)) ?? {};
    const tracks = (await getArtistTracks(soundchartsId)) ?? [];

    debug({
      requestId,
      artistId: artist.id,
      msg: 'Updating artist with Soundcharts data',
    });

    await db
      .update(artists)
      .set({
        metadata,
        streaming,
        followers,
        tracks,
        updated: new Date(),
      })
      .where(eq(artists.id, artist.id));

    debug({
      requestId,
      artistId: artist.id,
      msg: 'Artist update completed successfully',
    });

    return { artistId: artist.id, success: true };
  } catch (error) {
    debug({
      requestId,
      artistId: artist.id,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Error during artist update',
    });
    return {
      artistId: artist.id,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

export async function enrichWithSoundcharts(artistData: (typeof artists.$inferSelect)[]) {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      msg: 'Starting soundcharts enrichment process',
    });

    if (!artistData.length) {
      debug({
        requestId,
        msg: 'No artists found to update with Soundcharts',
      });
      return {
        success: true,
        message: 'No artists found to update',
        updates: [],
      };
    }

    const updates = await Promise.all(artistData.map((artist) => updateArtist(artist)));

    debug({
      requestId,
      updateCount: updates.length,
      successCount: updates.filter((u) => u.success).length,
      msg: 'Completed soundcharts enrichment process',
    });

    return { success: true, updates };
  } catch (err) {
    debug({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in soundcharts enrichment',
    });
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}
