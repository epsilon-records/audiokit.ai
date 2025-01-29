import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import { getMusicfetchData } from '../integrations/musicfetch.js';
import { eq } from 'drizzle-orm';
import logger from '../../utils/logger.js';
import { sanitizeUrl } from '../../utils/sanitize.js';
import { serializeError } from 'serialize-error';
import { inspect } from 'node:util';

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

  logger.info(`🎬 Starting Musicfetch enrichment process`, {
    requestId,
    artistCount: artistData.length,
    metadata: {
      environment: process.env.NODE_ENV,
      musicfetchUrl: process.env.MUSICFETCH_BASE_URL ? '✅ Configured' : '❌ Missing',
      musicfetchToken: process.env.MUSICFETCH_TOKEN ? '✅ Configured' : '❌ Missing',
    },
  });

  try {
    if (!artistData.length) {
      logger.warn(`🛑 No artists found to update with Musicfetch`, { requestId });
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
          logger.info(`🎬 Starting artist update`, artistContext);

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
            logger.warn(`⚠️ No valid service link found for artist`, artistContext);
            return {
              artistId: artist.id,
              success: false,
              error: 'No valid service link found',
              details: artistContext,
            };
          }

          const musicfetchBaseUrl = process.env.MUSICFETCH_BASE_URL;
          if (!musicfetchBaseUrl) {
            logger.error(`❌ Musicfetch base URL not configured`, artistContext);
            return {
              artistId: artist.id,
              success: false,
              error: 'Musicfetch service not configured',
              details: artistContext,
            };
          }

          logger.info(`🔍 Fetching Musicfetch data`, {
            ...artistContext,
            sourceUrl: linkUrl,
          });

          const services = await getMusicfetchData(linkUrl, []);
          await db.update(artists).set({ services }).where(eq(artists.id, artist.id));

          const updateFields: Record<string, string> = {};

          for (const service in services) {
            const serviceLink = services[service]?.link;
            if (serviceLink && typeof serviceLink === 'string' && serviceLink.trim() !== '') {
              if (
                service === 'spotify' ||
                service === 'appleMusic' ||
                service === 'soundcloud' ||
                service === 'youtube' ||
                service === 'bandcamp' ||
                service === 'facebook' ||
                service === 'instagram' ||
                service === 'tiktok' ||
                service === 'x'
              ) {
                updateFields[service] = sanitizeUrl(serviceLink);
              }
            }
          }

          logger.info(`🔄 Updating artist with Musicfetch data`, {
            ...artistContext,
            updateFields: Object.keys(updateFields),
            serviceCount: Object.keys(services).length,
          });

          await db.update(artists).set(updateFields).where(eq(artists.id, artist.id));

          logger.info(`✅ Successfully updated artist with Musicfetch data`, {
            ...artistContext,
            duration: Date.now() - artistStartTime,
            updatedFields: Object.keys(updateFields),
            serviceCount: Object.keys(services).length,
          });

          return {
            artistId: artist.id,
            success: true,
            details: {
              updatedFields: Object.keys(updateFields),
              serviceCount: Object.keys(services).length,
            },
          };
        } catch (err) {
          const serializedError = serializeError(err);
          logger.error(`❌ Error updating artist with Musicfetch`, {
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
            artistId: artist.id,
            success: false,
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
      `🏁 Completed Musicfetch enrichment process`,
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
    logger.error(`💥 Critical error in Musicfetch enrichment process`, {
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
