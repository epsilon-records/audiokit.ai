import { eq } from 'drizzle-orm';
import { serializeError } from 'serialize-error';
import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import logger from '../../utils/logger.js';
import { getMusicfetchData } from '../integrations/musicfetch.js';

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

export async function enrichWithMusicfetch(
  artistData: (typeof artists.$inferSelect)[]
): Promise<EnrichmentResult> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  logger.start(requestId, 'Starting Musicfetch enrichment process', {
    artistCount: artistData.length,
    metadata: {
      environment: process.env.NODE_ENV,
      musicfetchUrl: process.env.MUSICFETCH_API_BASE ? '✅ Configured' : '❌ Missing',
      musicfetchApiKey: process.env.MUSICFETCH_API_KEY ? '✅ Configured' : '❌ Missing',
    },
  });

  try {
    if (!artistData.length) {
      logger.warning(requestId, 'No artists found to update with Musicfetch', undefined, {
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
          existingLinks: {
            spotify: artist.spotify ? '✅ Present' : '❌ Missing',
            appleMusic: artist.appleMusic ? '✅ Present' : '❌ Missing',
            soundcloud: artist.soundcloud ? '✅ Present' : '❌ Missing',
            youtube: artist.youtube ? '✅ Present' : '❌ Missing',
            bandcamp: artist.bandcamp ? '✅ Present' : '❌ Missing',
            facebook: artist.facebook ? '✅ Present' : '❌ Missing',
            instagram: artist.instagram ? '✅ Present' : '❌ Missing',
            tiktok: artist.tiktok ? '✅ Present' : '❌ Missing',
            x: artist.x ? '✅ Present' : '❌ Missing',
          },
        };

        try {
          logger.start(requestId, 'Starting artist update', artistContext);

          const serviceLinks = [
            artist.spotify,
            artist.appleMusic,
            artist.soundcloud,
            artist.youtube,
            artist.bandcamp,
            artist.facebook,
            artist.instagram,
            artist.tiktok,
            artist.x,
          ];

          const linkUrl = serviceLinks.find((link) => link !== null && link !== '');

          if (!linkUrl) {
            logger.warning(
              requestId,
              'No valid service links found for artist',
              undefined,
              artistContext
            );
            return {
              success: false,
              artistId: artist.id,
              error: 'No valid service links found',
              details: artistContext,
            };
          }

          logger.process(
            requestId,
            'Fetching artist links from Musicfetch',
            {
              sourceLink: linkUrl,
            },
            artistContext
          );

          const links = await getMusicfetchData(linkUrl, [
            'spotify',
            'appleMusic',
            'soundcloud',
            'youtube',
            'bandcamp',
            'facebook',
            'instagram',
            'tiktok',
            'x',
          ]);

          if (!links) {
            logger.warning(requestId, 'No links found from Musicfetch', undefined, artistContext);
            return {
              success: false,
              artistId: artist.id,
              error: 'No links found from Musicfetch',
              details: artistContext,
            };
          }

          // Add validation for link values
          const validatedLinks = Object.fromEntries(
            Object.entries(links).map(([key, value]) => {
              if (typeof value !== 'string') {
                logger.warning(
                  requestId,
                  `Invalid link format for ${key}`,
                  { value },
                  artistContext
                );
                return [key, null]; // Set to null if invalid
              }
              return [key, value];
            })
          );

          logger.process(
            requestId,
            'Updating artist with Musicfetch data',
            {
              linksFound: Object.keys(validatedLinks).length,
            },
            artistContext
          );

          await db
            .update(artists)
            .set({
              ...validatedLinks,
              updated: new Date(),
            })
            .where(eq(artists.id, artist.id));

          logger.success(
            requestId,
            'Successfully updated artist with Musicfetch data',
            {
              duration: Date.now() - artistStartTime,
              linksUpdated: Object.keys(validatedLinks),
            },
            artistContext
          );

          return {
            success: true,
            artistId: artist.id,
            details: artistContext,
          };
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
      'Completed Musicfetch enrichment process',
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
    logger.error(requestId, 'Critical error in Musicfetch enrichment process', serializedError, {
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
