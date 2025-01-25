import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import { getMusicfetchData } from '../musicfetch.js';
import { eq } from 'drizzle-orm';
import { debug } from '../../utils/logger.js';
import { error } from '@sveltejs/kit';
import { sanitizeUrl } from '../../utils/sanitize.js';

export async function enrichWithMusicfetch(artistData: (typeof artists.$inferSelect)[]) {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      msg: 'Starting Musicfetch enrichment process',
    });

    if (!artistData.length) {
      debug({
        requestId,
        msg: 'No artists found to update with Musicfetch',
      });
      return {
        success: true,
        message: 'No artists found to update',
        updates: [],
      };
    }

    const updates = await Promise.all(
      artistData.map(async (artist) => {
        try {
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
            debug({
              requestId,
              artistId: artist.id,
              msg: 'No valid service link found for artist',
            });
            return { artistId: artist.id, success: false, error: 'No valid service link found' };
          }

          const services = await getMusicfetchData(linkUrl, []);
          await db.update(artists).set({ services }).where(eq(artists.id, artist.id));

          const updateFields: {
            spotify?: string;
            appleMusic?: string;
            soundcloud?: string;
            youtube?: string;
            bandcamp?: string;
            facebook?: string;
            instagram?: string;
            tiktok?: string;
            x?: string;
          } = {};

          for (const service in services) {
            if (services[service]?.link) {
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
                updateFields[service] = sanitizeUrl(services[service].link);
              }
            }
          }

          console.log(updateFields);

          await db.update(artists).set(updateFields).where(eq(artists.id, artist.id));

          debug({
            requestId,
            artistId: artist.id,
            msg: 'Updated artist with Musicfetch data',
          });

          return { artistId: artist.id, success: true };
        } catch (error) {
          debug({
            requestId,
            artistId: artist.id,
            error: error instanceof Error ? error.message : 'Unknown error',
            msg: 'Error updating artist with Musicfetch',
          });
          return {
            artistId: artist.id,
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
          };
        }
      })
    );

    debug({
      requestId,
      updateCount: updates.length,
      successCount: updates.filter((u) => u.success).length,
      msg: 'Completed Musicfetch enrichment process',
    });

    return { success: true, updates };
  } catch (err) {
    debug({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in Musicfetch enrichment',
    });
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}
