import { eq } from 'drizzle-orm';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';
import { db } from '../../db/index.js';
import { artists } from '../../db/schema.js';
import logger from '../../utils/logger.js';
import { sanitizeUrl } from '../../utils/sanitize.js';
import { getHubspotData, syncToHubspot } from '../integrations/hubspot.js';

interface SerializedErrorWithCode extends Error {
  code?: string | number;
}

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
    logger.error(requestId, 'No email found for artist', new Error('MISSING_EMAIL'), {
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
  logger.process(requestId, 'Building updates for artist', {
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
  logger.process(requestId, 'Applying updates to artist', {
    artistId: artist.id,
    email: artist.email,
    updateFields: Object.keys(updates),
  });

  try {
    // First update our database
    await db.update(artists).set(updates).where(eq(artists.id, artist.id));

    // Check if we need to update Hubspot with sanitized URLs
    const urlFields = ['website', 'spotify', 'appleMusic', 'soundcloud', 'bandcamp', 'instagram'];
    const hubspotUpdates: Record<string, string> = {};

    urlFields.forEach((field) => {
      const value = artist[field as keyof typeof artist];
      if (value && typeof value === 'string') {
        hubspotUpdates[field] = sanitizeUrl(value);
      }
    });

    if (artist.email && Object.keys(hubspotUpdates).length > 0) {
      logger.process(requestId, 'Updating Hubspot with sanitized URLs', {
        artistId: artist.id,
        updates: hubspotUpdates,
      });
      await syncToHubspot(artist.email, hubspotUpdates);
    } else if (!artist.email) {
      logger.warning(requestId, 'No email found for artist', {
        artistId: artist.id,
      });
      return;
    } else {
      logger.warning(requestId, 'No Hubspot updates to apply', {
        artistId: artist.id,
        email: artist.email,
      });
    }

    logger.success(requestId, 'Successfully merged Hubspot data', {
      artistId: artist.id,
      email: artist.email,
      updateFields: Object.keys(updates),
      duration: Date.now() - startTime,
    });
  } catch (err) {
    const serializedError = serializeError(err) as SerializedErrorWithCode;
    logger.error(requestId, 'Failed to apply updates', serializedError, {
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

async function updateHubspotArtist(artist: typeof artists.$inferSelect & { email: string }) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    artistId: artist.id,
    artistName: artist.stageName,
    email: artist.email,
  };

  logger.start(requestId, 'Starting Hubspot artist update', context);

  try {
    const emailValidationError = validateArtistEmail(artist, requestId);
    if (emailValidationError) return emailValidationError;

    const hubspotData = await getHubspotData(artist.email);
    if (!hubspotData || !hubspotData.properties) {
      logger.warning(requestId, 'No Hubspot data available', undefined, context);
      return {
        artistId: artist.id,
        email: artist.email,
        success: false,
        error: 'No Hubspot data available',
      };
    }

    logger.data(requestId, 'Retrieved Hubspot contact data', {
      hubspotId: hubspotData.id,
      availableFields: Object.keys(hubspotData.properties),
    });

    const updates = buildUpdateFields(artist, { properties: hubspotData.properties }, requestId);
    await applyUpdates(artist, updates, requestId);

    logger.success(
      requestId,
      'Successfully updated artist in Hubspot',
      {
        duration: Date.now() - startTime,
      },
      context
    );

    return {
      success: true,
      artistId: artist.id,
      details: context,
    };
  } catch (err) {
    const serializedError = serializeError(err) as SerializedErrorWithCode;
    logger.error(requestId, 'Error processing artist in Hubspot', serializedError, {
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

export async function enrichWithHubspot(
  artistData: (typeof artists.$inferSelect)[]
): Promise<EnrichmentResult> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  logger.start(requestId, 'Starting Hubspot enrichment process', {
    artistCount: artistData.length,
    metadata: {
      environment: process.env.NODE_ENV,
      hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
      hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
    },
  });

  try {
    if (!artistData.length) {
      logger.warning(requestId, 'No artists found to update with Hubspot', undefined, {
        requestId,
      });
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

    logger[successCount === updates.length ? 'success' : 'warning'](
      requestId,
      'Completed Hubspot enrichment process',
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
    const serializedError = serializeError(err) as SerializedErrorWithCode;
    logger.error(requestId, 'Critical error in Hubspot enrichment process', serializedError, {
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
