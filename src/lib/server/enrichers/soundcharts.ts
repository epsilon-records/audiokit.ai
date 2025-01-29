import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import {
  getArtistIdFromSpotify,
  getArtistStats,
  getArtistTracks,
} from '../integrations/soundcharts.js';
import { eq } from 'drizzle-orm';
import logger from '../../utils/logger.js';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';

interface EnrichmentResult {
  success: boolean;
  message?: string;
  error?: string;
  details?: Record<string, unknown>;
  updates: Array<{
    artistId: string;
    success: boolean;
    error?: string;
    details?: Record<string, unknown>;
  }>;
}

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
  const startTime = Date.now();
  const artistContext = {
    requestId,
    artistId: artist.id,
    artistName: artist.stageName,
    existingSoundchartsId: artist.soundchartsId ? '✅ Present' : '❌ Missing',
    spotifyUrl: artist.spotify ? '✅ Present' : '❌ Missing',
  };

  logger.info(`🎬 Starting Soundcharts artist update`, artistContext);

  try {
    let soundchartsId = artist.soundchartsId;

    if (!soundchartsId && artist.spotify) {
      logger.info(`🔍 Attempting to get Soundcharts ID from Spotify URL`, artistContext);

      const spotifyId = extractSpotifyId(artist.spotify);
      if (!spotifyId) {
        logger.warn(`⚠️ Could not extract Spotify ID from URL`, artistContext);
        throw new Error('Invalid Spotify URL format');
      }

      soundchartsId = await getArtistIdFromSpotify(spotifyId);
      if (soundchartsId) {
        logger.info(`✅ Successfully retrieved Soundcharts ID`, {
          ...artistContext,
          newSoundchartsId: '✅ Retrieved',
        });
        await db.update(artists).set({ soundchartsId }).where(eq(artists.id, artist.id));
      } else {
        logger.warn(`⚠️ No Soundcharts ID found for Spotify ID`, artistContext);
      }
    }

    if (!soundchartsId) {
      logger.error(`❌ No Soundcharts ID available`, artistContext);
      return {
        success: false,
        artistId: artist.id,
        error: 'No Soundcharts ID available',
        details: artistContext,
      };
    }

    logger.info(`📊 Fetching Soundcharts stats`, {
      ...artistContext,
      soundchartsId: '✅ Present', // Don't log actual ID
    });

    const [stats, tracks] = await Promise.all([
      getArtistStats(soundchartsId),
      getArtistTracks(soundchartsId),
    ]);

    if (!stats || !tracks) {
      logger.error(`❌ Failed to fetch Soundcharts data`, {
        ...artistContext,
        statsAvailable: !!stats,
        tracksAvailable: !!tracks,
      });
      throw new Error('Failed to fetch Soundcharts data');
    }

    logger.info(`🔄 Updating artist with Soundcharts data`, {
      ...artistContext,
      metadataKeys: Object.keys(stats.metadata || {}).length,
      streamingMetrics: Object.keys(stats.streaming || {}).length,
      followerMetrics: Object.keys(stats.followers || {}).length,
      trackCount: tracks.items.length,
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

    logger.info(`✅ Successfully updated artist with Soundcharts data`, {
      ...artistContext,
      duration: Date.now() - startTime,
      updateTypes: ['metadata', 'streaming', 'followers', 'tracks'],
    });

    return {
      success: true,
      artistId: artist.id,
      details: artistContext,
    };
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`❌ Error during Soundcharts artist update`, {
      ...artistContext,
      error: {
        message: serializedError.message,
        stack: serializedError.stack,
        type: serializedError.name,
        code: serializedError.code,
        additionalInfo: inspect(serializedError, { depth: null }),
      },
      duration: Date.now() - startTime,
    });

    return {
      success: false,
      artistId: artist.id,
      error: serializedError.message,
      details: {
        error: serializedError,
        context: artistContext,
      },
    };
  }
}

export async function enrichWithSoundcharts(
  artistData: (typeof artists.$inferSelect)[]
): Promise<EnrichmentResult> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  logger.info(`🎬 Starting Soundcharts enrichment process`, {
    requestId,
    artistCount: artistData.length,
    metadata: {
      environment: process.env.NODE_ENV,
      soundchartsUrl: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
      soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
      soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
    },
  });

  try {
    if (!artistData.length) {
      logger.warn(`🛑 No artists found to update with Soundcharts`, { requestId });
      return {
        success: true,
        message: 'No artists found to update',
        updates: [],
      };
    }

    const updates = await Promise.all(
      artistData.map(async (artist) => {
        const artistStartTime = Date.now();
        const artistContext = {
          requestId,
          artistId: artist.id,
          artistName: artist.stageName,
          existingSoundchartsId: artist.soundchartsId ? '✅ Present' : '❌ Missing',
          spotifyUrl: artist.spotify ? '✅ Present' : '❌ Missing',
        };

        try {
          logger.info(`🎬 Starting artist update`, artistContext);

          const result = await updateArtist(artist);

          logger.info(`✅ Successfully processed artist`, {
            ...artistContext,
            duration: Date.now() - artistStartTime,
            success: result.success,
          });

          return result;
        } catch (err) {
          const serializedError = serializeError(err);
          logger.error(`❌ Error processing artist`, {
            ...artistContext,
            error: {
              message: serializedError.message,
              stack: serializedError.stack,
              type: serializedError.name,
              code: serializedError.code,
              additionalInfo: inspect(serializedError, { depth: null }),
            },
            duration: Date.now() - artistStartTime,
          });

          return {
            success: false,
            artistId: artist.id,
            error: serializedError.message,
            details: {
              error: serializedError,
              context: artistContext,
            },
          };
        }
      })
    );

    const successCount = updates.filter((u) => u.success).length;
    const failureCount = updates.length - successCount;

    logger[successCount === updates.length ? 'info' : 'warn'](
      `🏁 Completed Soundcharts enrichment process`,
      {
        requestId,
        duration: Date.now() - startTime,
        totalArtists: updates.length,
        successCount,
        failureCount,
        successRate: `${((successCount / updates.length) * 100).toFixed(2)}%`,
        failures: updates
          .filter((u) => !u.success)
          .map((u) => ({
            artistId: u.artistId,
            error: u.error,
            details: u.details,
          })),
      }
    );

    return {
      success: successCount > 0,
      updates,
      message:
        successCount === updates.length
          ? 'All artists updated successfully'
          : `Updated ${successCount} of ${updates.length} artists`,
    };
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Critical error in Soundcharts enrichment process`, {
      requestId,
      duration: Date.now() - startTime,
      error: {
        message: serializedError.message,
        stack: serializedError.stack,
        type: serializedError.name,
        code: serializedError.code,
        additionalInfo: inspect(serializedError, { depth: null }),
      },
      input: {
        artistCount: artistData.length,
        sampleArtist: artistData[0]
          ? {
              id: artistData[0].id,
              name: artistData[0].stageName,
            }
          : null,
      },
    });

    return {
      success: false,
      error: serializedError.message,
      updates: [],
      details: {
        error: serializedError,
        requestId,
        duration: Date.now() - startTime,
      },
    };
  }
}
