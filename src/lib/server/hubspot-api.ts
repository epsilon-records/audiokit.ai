import type { artistSchema } from '../schemas/artist.js';
import type { z } from 'zod';
import logger from '../utils/logger.js';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';

interface HubspotContact {
  id: string;
  properties: {
    email: string;
    phone?: string;
    city?: string;
    country?: string;
    website?: string;
    spotify?: string;
    instagram?: string;
    facebook?: string;
    x?: string;
    tiktok?: string;
    soundcloud?: string;
    youtube?: string;
    lifecyclestage?: string;
  };
}

// Define the type from the Zod schema
type Artist = z.infer<typeof artistSchema>;

/**
 * Fetches a contact from HubSpot by email
 */
export async function getHubspotContact(email: string): Promise<HubspotContact | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    email,
  };

  try {
    logger.info(`🔍 Searching for Hubspot contact`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
        hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
      },
    });

    // First search for the contact by email
    const searchResponse = await fetch(
      `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts/search`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.HUBSPOT_API_KEY}`,
        },
        body: JSON.stringify({
          filterGroups: [
            {
              filters: [
                {
                  propertyName: 'email',
                  operator: 'EQ',
                  value: email,
                },
              ],
            },
          ],
        }),
      }
    );

    if (!searchResponse.ok) {
      logger.error(`❌ Hubspot search API error`, {
        ...context,
        status: searchResponse.status,
        statusText: searchResponse.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const searchData = await searchResponse.json();
    logger.info(`📥 Retrieved Hubspot search results`, {
      ...context,
      resultsCount: searchData.results?.length || 0,
      duration: Date.now() - startTime,
    });

    if (!searchData.results?.length) {
      logger.info(`ℹ️ No Hubspot contact found`, context);
      return null;
    }

    // Get the contact ID from the search results
    const contactId = searchData.results[0].id;

    // Make a second request to get all properties
    const detailResponse = await fetch(
      `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts/${contactId}?properties=firstname,lastname,email,phone,city,country,biography,website,spotify,apple_music,twitterhandle,instagram,soundcloud`,
      {
        headers: {
          Authorization: `Bearer ${process.env.HUBSPOT_API_KEY}`,
        },
      }
    );

    if (!detailResponse.ok) {
      logger.error(`❌ Hubspot detail API error`, {
        ...context,
        contactId,
        status: detailResponse.status,
        statusText: detailResponse.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const detailData = await detailResponse.json();
    logger.info(`✅ Successfully retrieved Hubspot contact details`, {
      ...context,
      contactId,
      availableFields: Object.keys(detailData.properties),
      duration: Date.now() - startTime,
    });

    return {
      id: contactId,
      properties: detailData.properties,
    };
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching Hubspot contact`, {
      ...context,
      error: {
        message: serializedError.message,
        stack: serializedError.stack,
        type: serializedError.name,
        code: serializedError.code,
        additionalInfo: inspect(serializedError, { depth: null }),
      },
      duration: Date.now() - startTime,
    });
    return null;
  }
}

/**
 * Syncs artist data back to HubSpot
 */
export async function syncToHubspot(artist: Artist): Promise<void> {
  if (!artist.email) {
    return;
  }

  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    artistId: artist.id,
    email: artist.email,
  };

  try {
    logger.info(`🔄 Starting Hubspot sync`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
        hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
      },
    });

    // First try to find existing contact
    const existingContact = await getHubspotContact(artist.email);

    logger.info(`📥 Retrieved existing Hubspot contact status`, {
      ...context,
      contactExists: !!existingContact,
      contactId: existingContact?.id,
    });

    const endpoint = existingContact
      ? `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts/${existingContact.id}`
      : `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts`;

    const method = existingContact ? 'PATCH' : 'POST';

    const payload = {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.HUBSPOT_API_KEY}`,
      },
      body: {
        properties: {
          email: artist.email,
          phone: artist.phone,
          city: artist.city,
          country: artist.country,
          biography: artist.biography,
          website: artist.website,
          spotify: artist.spotify,
          instagram: artist.instagram,
          twitterhandle: artist.x,
          soundcloud: artist.soundcloud,
        },
      },
    };

    logger.info(`🔄 Syncing artist data to Hubspot`, {
      ...context,
      operation: existingContact ? 'UPDATE' : 'CREATE',
      updateFields: Object.keys(payload.body.properties).filter(
        (key) => payload.body.properties[key as keyof typeof payload.body.properties] !== undefined
      ),
    });

    const response = await fetch(endpoint, {
      method: payload.method,
      headers: payload.headers,
      body: JSON.stringify(payload.body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error(`❌ Hubspot sync API error`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
        errorText,
        duration: Date.now() - startTime,
      });
      throw new Error(`Hubspot API error: ${errorText}`);
    }

    const responseData = await response.json();
    logger.info(`✅ Successfully synced artist to Hubspot`, {
      ...context,
      contactId: responseData.id,
      duration: Date.now() - startTime,
    });
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error syncing to Hubspot`, {
      ...context,
      error: {
        message: serializedError.message,
        stack: serializedError.stack,
        type: serializedError.name,
        code: serializedError.code,
        additionalInfo: inspect(serializedError, { depth: null }),
      },
      duration: Date.now() - startTime,
    });
    // Don't throw the error - we don't want to break the main flow if HubSpot sync fails
  }
}
