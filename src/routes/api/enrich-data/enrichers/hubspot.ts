import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { getHubspotContact } from '$lib/server/hubspot';
import { eq } from 'drizzle-orm';
import { debug, warn } from '$lib/utils/logger';
import { error } from '@sveltejs/kit';

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
  facebook?: string;
  instagram?: string;
  mixcloud?: string;
  tiktok?: string;
  twitch?: string;
}

function validateArtistEmail(artist: typeof artists.$inferSelect, requestId: string) {
  if (!artist.email) {
    debug({
      requestId,
      artistId: artist.id,
      msg: 'No email found for artist',
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
  hubspotData: { properties: Record<string, string | null> }
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
    ['facebook', 'facebook'],
    ['instagram', 'instagram'],
    ['mixcloud', 'mixcloud'],
    ['tiktok', 'tiktok'],
    ['twitch', 'twitch'],
  ];

  fieldsToUpdate.forEach(([artistField, hubspotField]) => {
    if (properties[hubspotField]) {
      updates[artistField] = properties[hubspotField] as string;
    }
  });

  const { firstname, lastname } = properties;
  debug({
    artistId: artist.id,
    artistLegalName: artist.legalName,
    firstname,
    lastname,
    msg: 'Building updates',
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
  debug({
    requestId,
    email: artist.email,
    artistId: artist.id,
    updates,
    msg: 'Applying updates to artist',
  });

  await db.update(artists).set(updates).where(eq(artists.id, artist.id));

  debug({
    requestId,
    email: artist.email,
    artistId: artist.id,
    updates,
    msg: 'Merged Hubspot data',
  });
}

async function updateHubspotArtist(artist: typeof artists.$inferSelect) {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      email: artist.email,
      artistId: artist.id,
      msg: 'Starting Hubspot artist update',
    });

    const emailValidationError = validateArtistEmail(artist, requestId);
    if (emailValidationError) return emailValidationError;

    const hubspotData = await getHubspotContact(artist.email!);

    if (!hubspotData) {
      warn({
        requestId,
        email: artist.email,
        artistId: artist.id,
        msg: 'No Hubspot data available',
      });
      return {
        artistId: artist.id,
        email: artist.email,
        success: false,
        error: 'No Hubspot data available',
      };
    }

    debug({
      requestId,
      email: artist.email,
      artistId: artist.id,
      hubspotData,
      msg: 'Retrieved Hubspot contact data',
    });

    const updates = buildUpdateFields(artist, hubspotData);
    await applyUpdates(artist, updates, requestId);

    return { artistId: artist.id, email: artist.email, success: true, updates };
  } catch (error) {
    debug({
      requestId,
      email: artist.email,
      artistId: artist.id,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Error during Hubspot artist update',
    });
    return {
      artistId: artist.id,
      email: artist.email,
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

export async function enrichWithHubspot(artistData: (typeof artists.$inferSelect)[]) {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      msg: 'Starting Hubspot enrichment process',
    });

    if (!artistData.length) {
      debug({
        requestId,
        msg: 'No artists found to update with Hubspot',
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

    debug({
      requestId,
      updateCount: updates.length,
      successCount: updates.filter((u) => u.success).length,
      msg: 'Completed Hubspot enrichment process',
    });

    return { success: true, updates };
  } catch (err) {
    debug({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in Hubspot enrichment',
    });
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}
