import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { getArtistIdFromSpotify, getArtistStats } from '$lib/server/soundcharts';
import { getHubspotContact } from '$lib/server/hubspot';
import { error } from '@sveltejs/kit';
import { eq, not, or, and } from 'drizzle-orm';
import { debug, info, warn } from '$lib/utils/logger';

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
    debug({
      requestId,
      artistId: artist.id,
      msg: 'Starting artist update process',
    });

    let soundchartsId = artist.soundchartsId;
    debug({
      requestId,
      artistId: artist.id,
      soundchartsId,
      msg: 'Initial soundchartsId status',
    });

    if (!soundchartsId && artist.spotify) {
      debug({
        requestId,
        artistId: artist.id,
        spotifyUrl: artist.spotify,
        msg: 'Attempting to get soundchartsId from Spotify URL',
      });

      const spotifyId = extractSpotifyId(artist.spotify);
      if (spotifyId) {
        soundchartsId = await getArtistIdFromSpotify(spotifyId);

        if (soundchartsId) {
          debug({
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
      warn({
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

    debug({
      requestId,
      artistId: artist.id,
      soundchartsId,
      msg: 'Fetching Soundcharts stats',
    });

    const soundchartsData = await getArtistStats(soundchartsId);

    if (!soundchartsData) {
      warn({
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

    debug({
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

    debug({
      requestId,
      artistId: artist.id,
      msg: 'Artist update completed successfully',
    });

    return { artistId: artist.id, success: true };
  } catch (error) {
    debug({
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

async function getArtistsToUpdate() {
  const soundchartsArtists = await db
    .select()
    .from(artists)
    .where(or(not(eq(artists.spotify, '')), not(eq(artists.soundchartsId, ''))));

  const hubspotArtists = await db
    .select()
    .from(artists)
    .where(
      and(
        not(eq(artists.email, '')),
        or(eq(artists.city, ''), eq(artists.country, ''), eq(artists.website, ''))
      )
    );

  return {
    soundchartsArtists,
    hubspotArtists,
  };
}

async function enrichWithSoundcharts(artistData: (typeof artists.$inferSelect)[]) {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      msg: 'Starting soundcharts enrichment process',
    });

    if (!artistData.length) {
      debug({
        requestId,
        msg: 'No artists found to update with Soundcharts',
      });
      return {
        success: true,
        message: 'No artists found to update',
        updates: [],
      };
    }

    const updates = await Promise.all(artistData.map((artist) => updateArtist(artist)));

    debug({
      requestId,
      updateCount: updates.length,
      successCount: updates.filter((u) => u.success).length,
      msg: 'Completed soundcharts enrichment process',
    });

    return { success: true, updates };
  } catch (err) {
    debug({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in soundcharts enrichment',
    });
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}

interface HubspotUpdateFields {
  city?: string;
  country?: string;
  website?: string;
  phone?: string;
  legalName?: string;
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

  // Only update fields if they're empty or null in the database
  if ((!artist.city || artist.city === '') && hubspotData.properties.city) {
    updates.city = hubspotData.properties.city;
  }
  if ((!artist.country || artist.country === '') && hubspotData.properties.country) {
    updates.country = hubspotData.properties.country;
  }
  if ((!artist.website || artist.website === '') && hubspotData.properties.website) {
    updates.website = hubspotData.properties.website;
  }
  if ((!artist.phone || artist.phone === '') && hubspotData.properties.phone) {
    updates.phone = hubspotData.properties.phone;
  }

  // Combine first and last name for legal name if both exist
  const firstName = hubspotData.properties.firstname;
  const lastName = hubspotData.properties.lastname;
  if ((!artist.legalName || artist.legalName === '') && firstName && lastName) {
    updates.legalName = `${firstName} ${lastName}`;
  }

  return updates;
}

async function applyUpdates(
  artist: typeof artists.$inferSelect,
  updates: HubspotUpdateFields,
  requestId: string
) {
  info({
    requestId,
    email: artist.email,
    artistId: artist.id,
    updates,
    msg: 'Applying updates to artist',
  });

  await db.update(artists).set(updates).where(eq(artists.id, artist.id));

  info({
    requestId,
    email: artist.email,
    artistId: artist.id,
    updates,
    msg: 'Updated empty fields with Hubspot data',
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

async function enrichWithHubspot(artistData: (typeof artists.$inferSelect)[]) {
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

export async function GET() {
  const requestId = crypto.randomUUID();

  try {
    debug({
      requestId,
      msg: 'Starting data enrichment process',
    });

    const { soundchartsArtists, hubspotArtists } = await getArtistsToUpdate();

    const [soundchartsResults, hubspotResults] = await Promise.all([
      enrichWithSoundcharts(soundchartsArtists),
      enrichWithHubspot(hubspotArtists),
    ]);

    return new Response(
      JSON.stringify({
        success: true,
        soundcharts: soundchartsResults,
        hubspot: hubspotResults,
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (err) {
    debug({
      requestId,
      error: err instanceof Error ? err.message : 'Unknown error',
      msg: 'Error in data enrichment',
    });
    throw error(500, err instanceof Error ? err.message : 'Unknown error');
  }
}
