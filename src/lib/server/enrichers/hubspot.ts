import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import { getHubspotContact } from '../hubspot.js';
import { eq } from 'drizzle-orm';
import logger from '../../utils/logger.js';
import { error } from '@sveltejs/kit';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';

interface HubspotUpdateFields {
  city?: string;
  country?: string;
  website?: string;
  phone?: string;
  legalName?: string;
  spotify?: string;
  appleMusic?: string;
  soundcloud?: string;
  bandcamp?: string;
  instagram?: string;
}

function validateArtistEmail(artist: typeof artists.$inferSelect, requestId: string) {
  if (!artist.email) {
    logger.error(`❌ No email found for artist`, {
      requestId,
      artistId: artist.id,
      error: 'MISSING_EMAIL',
    });
    return {
      artistId: artist.id,
      email: artist.email,
      success: false,
      error: 'No email found for artist',
    };
  }
  return null;
}

function buildUpdateFields(
  artist: typeof artists.$inferSelect,
  hubspotData: { properties: Record<string, string | null> },
  requestId: string
): HubspotUpdateFields {
  const updates: HubspotUpdateFields = {};
  const { properties } = hubspotData;

  const fieldsToUpdate: [keyof HubspotUpdateFields, keyof typeof properties][] = [
    ['city', 'city'],
    ['country', 'country'],
    ['website', 'website'],
    ['phone', 'phone'],
    ['spotify', 'spotify'],
    ['appleMusic', 'apple_music'],
    ['soundcloud', 'soundcloud'],
    ['bandcamp', 'bandcamp'],
    ['instagram', 'instagram'],
  ];

  fieldsToUpdate.forEach(([artistField, hubspotField]) => {
    if (properties[hubspotField]) {
      updates[artistField] = properties[hubspotField] as string;
    }
  });

  const { firstname, lastname } = properties;
  logger.info(`🔄 Building updates for artist`, {
    requestId,
    artistId: artist.id,
    artistLegalName: artist.legalName,
    firstname,
    lastname,
    fieldsToUpdate: Object.keys(updates),
  });

  if (!artist.legalName && firstname && lastname) {
    updates.legalName = `${firstname} ${lastname}`;
  }

  return updates;
}

async function applyUpdates(
  artist: typeof artists.$inferSelect,
  updates: HubspotUpdateFields,
  requestId: string
) {
  const startTime = Date.now();
  logger.info(`🔄 Applying updates to artist`, {
    requestId,
    artistId: artist.id,
    email: artist.email,
    updateFields: Object.keys(updates),
  });

  try {
    await db.update(artists).set(updates).where(eq(artists.id, artist.id));

    logger.info(`✅ Successfully merged Hubspot data`, {
      requestId,
      artistId: artist.id,
      email: artist.email,
      updateFields: Object.keys(updates),
      duration: Date.now() - startTime,
    });
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`❌ Failed to apply updates`, {
      requestId,
      artistId: artist.id,
      email: artist.email,
      error: {
        message: serializedError.message,
        stack: serializedError.stack,
        type: serializedError.name,
        code: serializedError.code,
        additionalInfo: inspect(serializedError, { depth: null }),
      },
      duration: Date.now() - startTime,
    });
    throw err;
  }
}

async function updateHubspotArtist(artist: typeof artists.$inferSelect) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const artistContext = {
    requestId,
    artistId: artist.id,
    email: artist.email,
  };

  logger.info(`🎬 Starting Hubspot artist update`, artistContext);

  try {
    const emailValidationError = validateArtistEmail(artist, requestId);
    if (emailValidationError) return emailValidationError;

    const hubspotData = await getHubspotContact(artist.email!);

    if (!hubspotData) {
      logger.warn(`⚠️ No Hubspot data available`, artistContext);
      return {
        artistId: artist.id,
        email: artist.email,
        success: false,
        error: 'No Hubspot data available',
      };
    }

    logger.info(`📥 Retrieved Hubspot contact data`, {
      ...artistContext,
      hubspotId: hubspotData.id,
      availableFields: Object.keys(hubspotData.properties),
    });

    const updates = buildUpdateFields(artist, hubspotData, requestId);
    await applyUpdates(artist, updates, requestId);

    logger.info(`🎉 Successfully updated artist with Hubspot data`, {
      ...artistContext,
      duration: Date.now() - startTime,
      updateFields: Object.keys(updates),
    });

    return { artistId: artist.id, email: artist.email, success: true, updates };
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error during Hubspot artist update`, {
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
      artistId: artist.id,
      email: artist.email,
      success: false,
      error: serializedError.message,
    };
  }
}

export async function enrichWithHubspot(artistData: (typeof artists.$inferSelect)[]) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  logger.info(`🎬 Starting Hubspot enrichment process`, {
    requestId,
    artistCount: artistData.length,
    metadata: {
      environment: process.env.NODE_ENV,
      hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
      hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
    },
  });

  try {
    if (!artistData.length) {
      logger.warn(`🛑 No artists found to update with Hubspot`, { requestId });
      return {
        success: true,
        message: 'No artists found to update',
        updates: [],
      };
    }

    const updates = await Promise.all(
      artistData
        .filter((artist): artist is typeof artist & { email: string } => artist.email !== null)
        .map((artist) => updateHubspotArtist(artist))
    );

    const successCount = updates.filter((u) => u.success).length;
    const failureCount = updates.length - successCount;

    logger[successCount === updates.length ? 'info' : 'warn'](
      `🏁 Completed Hubspot enrichment process`,
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
    logger.error(`💥 Critical error in Hubspot enrichment process`, {
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
              email: artistData[0].email,
            }
          : null,
      },
    });
    throw error(500, serializedError.message);
  }
}
