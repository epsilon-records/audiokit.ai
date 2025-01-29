import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import { getArtistIdFromSpotify, getArtistStats, getArtistTracks } from '../soundcharts.js';
import { eq } from 'drizzle-orm';
import logger from '../../utils/logger.js';

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
  logger.info({
    requestId,
    artistId: artist.id,
    msg: '🎬 Starting artist update process',
    context: {
      artistName: artist.stageName,
      spotifyUrl: artist.spotify,
      existingSoundchartsId: artist.soundchartsId,
    },
  });

  try {
    let soundchartsId = artist.soundchartsId;

    if (!soundchartsId && artist.spotify) {
      logger.info({
        requestId,
        artistId: artist.id,
        msg: '🔍 Attempting to get Soundcharts ID from Spotify URL',
        context: {
          spotifyUrl: artist.spotify,
        },
      });

      const spotifyId = extractSpotifyId(artist.spotify);
      if (!spotifyId) {
        logger.warn({
          requestId,
          artistId: artist.id,
          msg: '⚠️ Could not extract Spotify ID from URL',
          context: {
            spotifyUrl: artist.spotify,
          },
        });
        throw new Error('Invalid Spotify URL format');
      }

      soundchartsId = await getArtistIdFromSpotify(spotifyId);
      if (soundchartsId) {
        logger.info({
          requestId,
          artistId: artist.id,
          msg: '✅ Successfully retrieved Soundcharts ID',
          context: {
            newSoundchartsId: soundchartsId,
          },
        });
        await db.update(artists).set({ soundchartsId }).where(eq(artists.id, artist.id));
      } else {
        logger.warn({
          requestId,
          artistId: artist.id,
          msg: '⚠️ No Soundcharts ID found for Spotify ID',
          context: {
            spotifyId,
          },
        });
      }
    }

    if (!soundchartsId) {
      logger.error({
        requestId,
        artistId: artist.id,
        msg: '❌ No Soundcharts ID available',
        context: {
          artistName: artist.stageName,
        },
      });
      return {
        success: false,
        error: 'No Soundcharts ID available',
        context: {
          spotifyUrl: artist.spotify,
          existingSoundchartsId: artist.soundchartsId,
        },
      };
    }

    logger.info({
      requestId,
      artistId: artist.id,
      msg: '📊 Fetching Soundcharts stats',
      context: {
        soundchartsId,
      },
    });

    const stats = await getArtistStats(soundchartsId);
    const tracks = await getArtistTracks(soundchartsId);

    if (!stats || !tracks) {
      logger.error({
        requestId,
        artistId: artist.id,
        msg: '❌ Failed to fetch Soundcharts data',
        context: {
          soundchartsId,
          statsAvailable: !!stats,
          tracksAvailable: !!tracks,
        },
      });
      throw new Error('Failed to fetch Soundcharts data');
    }

    logger.info({
      requestId,
      artistId: artist.id,
      msg: '🔄 Updating artist with Soundcharts data',
      context: {
        metadataKeys: Object.keys(stats.metadata || {}),
        streamingMetrics: Object.keys(stats.streaming || {}),
        followerMetrics: Object.keys(stats.followers || {}),
        trackCount: tracks.items.length,
      },
    });

    await db
      .update(artists)
      .set({
        metadata: stats.metadata || {},
        streaming: stats.streaming || {},
        followers: stats.followers || {},
        tracks: tracks || [],
        updated: new Date(),
      })
      .where(eq(artists.id, artist.id));

    logger.info({
      requestId,
      artistId: artist.id,
      msg: '🎉 Artist update completed successfully',
      context: {
        artistName: artist.stageName,
      },
    });

    return {
      success: true,
      context: {
        metadataKeys: Object.keys(stats.metadata || {}),
        trackCount: tracks.items.length,
      },
    };
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    logger.error({
      requestId,
      artistId: artist.id,
      msg: '🔥 Error during artist update',
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name,
      },
      context: {
        artistName: artist.stageName,
        soundchartsId: artist.soundchartsId,
        spotifyUrl: artist.spotify,
      },
    });
    return {
      success: false,
      error: error.message,
      stack: error.stack,
      context: {
        artistName: artist.stageName,
        soundchartsId: artist.soundchartsId,
      },
    };
  }
}

export async function enrichWithSoundcharts(artistData: (typeof artists.$inferSelect)[]) {
  const requestId = crypto.randomUUID();
  logger.info({
    requestId,
    msg: '🚀 Starting soundcharts enrichment process',
    context: {
      artistCount: artistData.length,
      artistIds: artistData.map((a) => a.id),
    },
  });

  try {
    if (!artistData.length) {
      logger.warn({
        requestId,
        msg: '🛑 No artists found to update with Soundcharts',
      });
      return {
        success: true,
        message: 'No artists found to update',
        updates: [],
        context: {
          requestId,
        },
      };
    }

    const updates = await Promise.all(artistData.map((artist) => updateArtist(artist)));
    const successfulUpdates = updates.filter((u) => u.success);
    const failedUpdates = updates.filter((u) => !u.success);

    logger.info({
      requestId,
      msg: '🏁 Completed soundcharts enrichment process',
      context: {
        artistCount: artistData.length,
        artistIds: artistData.map((a) => a.id),
        stats: {
          total: updates.length,
          successful: successfulUpdates.length,
          failed: failedUpdates.length,
        },
      },
    });

    return {
      success: failedUpdates.length === 0,
      updates,
      stats: {
        total: updates.length,
        successful: successfulUpdates.length,
        failed: failedUpdates.length,
      },
      context: {
        requestId,
      },
    };
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    logger.error({
      requestId,
      msg: '💥 Critical error in soundcharts enrichment',
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name,
      },
      context: {
        artistCount: artistData.length,
        artistIds: artistData.map((a) => a.id),
      },
    });

    return {
      success: false,
      error: error.message,
      stack: error.stack,
      context: {
        requestId,
      },
    };
  }
}
