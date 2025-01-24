import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { soundcharts } from '$lib/server/soundcharts';
import { error } from '@sveltejs/kit';
import { eq, not, or } from 'drizzle-orm';
import logger from '$lib/utils/logger';

// Extract Spotify ID from URL
function extractSpotifyId(spotifyUrl: string): string | null {
  try {
    const id = spotifyUrl.split('/').pop();
    return id || null;
  } catch {
    return null;
  }
}

// Update single artist
async function updateArtist(artist: typeof artists.$inferSelect) {
  const requestId = crypto.randomUUID();

  try {
    logger.info({
      requestId,
      artistId: artist.id,
      msg: 'Starting artist update process',
    });

    let soundchartsId = artist.soundchartsId;
    logger.debug({
      requestId,
      artistId: artist.id,
      soundchartsId,
      msg: 'Initial soundchartsId status',
    });

    if (!soundchartsId && artist.spotify) {
      logger.info({
        requestId,
        artistId: artist.id,
        spotifyUrl: artist.spotify,
        msg: 'Attempting to get soundchartsId from Spotify URL',
      });

      const spotifyId = extractSpotifyId(artist.spotify);
      if (spotifyId) {
        soundchartsId = await soundcharts.getArtistIdFromSpotify(spotifyId);

        if (soundchartsId) {
          logger.info({
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
      logger.warn({
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

    logger.info({
      requestId,
      artistId: artist.id,
      soundchartsId,
      msg: 'Fetching Soundcharts stats',
    });

    const soundchartsData = await soundcharts.getArtistStats(soundchartsId);

    if (!soundchartsData) {
      logger.warn({
        requestId,
        artistId: artist.id,
        msg: 'No Soundcharts data available',
      });
      return {
        artistId: artist.id,
        success: false,
        error: 'No Soundcharts data available',
      };
    }

    logger.info({
      requestId,
      artistId: artist.id,
      msg: 'Updating artist with Soundcharts data',
    });

    await db
      .update(artists)
      .set({
        metadata: soundchartsData.metadata,
        streaming: soundchartsData.streaming,
        followers: soundchartsData.followers,
        updated: new Date(),
      })
      .where(eq(artists.id, artist.id));

    logger.info({
      requestId,
      artistId: artist.id,
      msg: 'Artist update completed successfully',
    });

    return { artistId: artist.id, success: true };
  } catch (error) {
    logger.error({
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

export async function GET() {
  const requestId = crypto.randomUUID();

  try {
    logger.info({
      requestId,
      msg: 'Starting soundcharts enrichment cron',
    });

    const artistData = await db
      .select()
      .from(artists)
      .where(or(not(eq(artists.spotify, '')), not(eq(artists.soundchartsId, ''))));

    if (!artistData.length) {
      logger.info({
        requestId,
        msg: 'No artists found to update',
      });
      return new Response(
        JSON.stringify({
          success: true,
          message: 'No artists found to update',
          updates: [],
        }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    }

    logger.info({
      requestId,
      artistCount: artistData.length,
      msg: 'Processing artist updates',
    });

    const updates = await Promise.all(artistData.map((artist) => updateArtist(artist)));

    logger.info({
      requestId,
      updateCount: updates.length,
      successCount: updates.filter((u) => u.success).length,
      msg: 'Completed soundcharts enrichment process',
    });

    return new Response(JSON.stringify({ success: true, updates }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    logger.error({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in soundcharts enrichment',
    });
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}
