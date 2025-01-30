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
  const context = {
    artistId: artist.id,
    artistName: artist.stageName,
    existingSoundchartsId: artist.soundchartsId ? '✅ Present' : '❌ Missing',
    spotifyUrl: artist.spotify ? '✅ Present' : '❌ Missing',
  };

  logger.start(requestId, 'Starting Soundcharts artist update', context);

  try {
    let soundchartsId = artist.soundchartsId;

    if (!soundchartsId && artist.spotify) {
      logger.process(requestId, 'Attempting to get Soundcharts ID from Spotify URL', context);

      const spotifyId = extractSpotifyId(artist.spotify);
      if (!spotifyId) {
        logger.warning(requestId, 'Could not extract Spotify ID from URL', undefined, context);
        throw new Error('Invalid Spotify URL format');
      }

      soundchartsId = await getArtistIdFromSpotify(spotifyId);
      if (soundchartsId) {
        logger.success(
          requestId,
          'Successfully retrieved Soundcharts ID',
          { newSoundchartsId: '✅ Retrieved' },
          context
        );
        await db.update(artists).set({ soundchartsId }).where(eq(artists.id, artist.id));
      } else {
        logger.warning(requestId, 'No Soundcharts ID found for Spotify ID', undefined, context);
      }
    }

    if (!soundchartsId) {
      logger.error(
        requestId,
        'No Soundcharts ID available',
        new Error('No Soundcharts ID available'),
        context
      );
      return {
        success: false,
        artistId: artist.id,
        error: 'No Soundcharts ID available',
        details: context,
      };
    }

    logger.data(requestId, 'Fetching Soundcharts stats', { soundchartsId: '✅ Present' }, context);

    const [stats, tracks] = await Promise.all([
      getArtistStats(soundchartsId),
      getArtistTracks(soundchartsId),
    ]);

    if (!stats || !tracks) {
      logger.error(
        requestId,
        'Failed to fetch Soundcharts data',
        new Error('Failed to fetch Soundcharts data'),
        {
          ...context,
          statsAvailable: !!stats,
          tracksAvailable: !!tracks,
        }
      );
      throw new Error('Failed to fetch Soundcharts data');
    }

    logger.process(
      requestId,
      'Updating artist with Soundcharts data',
      {
        metadataKeys: Object.keys(stats.metadata || {}).length,
        streamingMetrics: Object.keys(stats.streaming || {}).length,
        followerMetrics: Object.keys(stats.followers || {}).length,
        trackCount: tracks.items.length,
      },
      context
    );

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

    logger.success(
      requestId,
      'Successfully updated artist with Soundcharts data',
      {
        duration: Date.now() - startTime,
        updateTypes: ['metadata', 'streaming', 'followers', 'tracks'],
      },
      context
    );

    return {
      success: true,
      artistId: artist.id,
      details: context,
    };
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error during Soundcharts artist update', serializedError, {
      ...context,
      duration: Date.now() - startTime,
    });

    return {
      success: false,
      artistId: artist.id,
      error: serializedError.message,
      details: {
        error: serializedError,
        context: context,
      },
    };
  }
}

export async function enrichWithSoundcharts(
  artistData: (typeof artists.$inferSelect)[]
): Promise<EnrichmentResult> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  logger.start(requestId, 'Starting Soundcharts enrichment process', {
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
      logger.warning(requestId, 'No artists found to update with Soundcharts', undefined, {
        requestId,
      });
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
          logger.start(requestId, 'Starting artist update', artistContext);

          const result = await updateArtist(artist);

          logger.success(
            requestId,
            'Successfully processed artist',
            {
              duration: Date.now() - artistStartTime,
              success: result.success,
            },
            artistContext
          );

          return result;
        } catch (err) {
          const serializedError = serializeError(err) as Error;
          logger.error(requestId, 'Error processing artist', serializedError, {
            ...artistContext,
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

    logger[successCount === updates.length ? 'success' : 'warning'](
      requestId,
      'Completed Soundcharts enrichment process',
      {
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
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Critical error in Soundcharts enrichment process', serializedError, {
      duration: Date.now() - startTime,
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
