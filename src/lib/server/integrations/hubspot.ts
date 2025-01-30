import type { artistSchema } from '../../schemas/artist.js';
import type { z } from 'zod';
import { logger } from '../../utils/logger.js';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';

interface HubspotContact {
  id: string;
  properties: {
    email: string;
    firstname?: string;
    lastname?: string;
    phone?: string;
    city?: string;
    country?: string;
    biography?: string;
    website?: string;
    spotify?: string;
    instagram?: string;
    twitterhandle?: string;
    soundcloud?: string;
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
    email,
    requestId,
  };

  logger.start(requestId, 'Fetching Hubspot contact', context);

  try {
    logger.process(
      requestId,
      'Searching for Hubspot contact',
      {
        metadata: {
          environment: process.env.NODE_ENV,
          hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
          hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
        },
      },
      context
    );

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
      logger.error(requestId, 'Hubspot search API error', new Error('API Error'), {
        ...context,
        status: searchResponse.status,
        statusText: searchResponse.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const searchData = await searchResponse.json();
    logger.data(requestId, 'Retrieved Hubspot search results', {
      resultsCount: searchData.results?.length || 0,
      duration: Date.now() - startTime,
    });

    if (!searchData.results?.length) {
      logger.warning(requestId, 'No Hubspot contact found', undefined, context);
      return null;
    }

    const contactId = searchData.results[0].id;

    const detailResponse = await fetch(
      `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts/${contactId}?properties=firstname,lastname,email,phone,city,country,biography,website,spotify,apple_music,twitterhandle,instagram,soundcloud`,
      {
        headers: {
          Authorization: `Bearer ${process.env.HUBSPOT_API_KEY}`,
        },
      }
    );

    if (!detailResponse.ok) {
      logger.error(requestId, 'Hubspot detail API error', new Error('API Error'), {
        ...context,
        contactId,
        status: detailResponse.status,
        statusText: detailResponse.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const contactData = await detailResponse.json();
    logger.success(requestId, 'Successfully retrieved Hubspot contact', {
      contactId,
      availableFields: Object.keys(contactData.properties),
      duration: Date.now() - startTime,
    });

    return contactData;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching Hubspot contact', serializedError, {
      ...context,
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

  logger.start(requestId, 'Starting Hubspot sync', {
    ...context,
    metadata: {
      environment: process.env.NODE_ENV,
      hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
      hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
    },
  });

  try {
    const existingContact = await getHubspotContact(artist.email);
    logger.process(requestId, 'Retrieved existing Hubspot contact status', {
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

    logger.process(requestId, 'Syncing artist data to Hubspot', {
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
      logger.error(requestId, 'Hubspot sync API error', new Error('API Error'), {
        ...context,
        status: response.status,
        statusText: response.statusText,
        errorText,
        duration: Date.now() - startTime,
      });
      throw new Error(`Hubspot API error: ${errorText}`);
    }

    const responseData = await response.json();
    logger.success(requestId, 'Successfully synced artist to Hubspot', {
      contactId: responseData.id,
      duration: Date.now() - startTime,
    });
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error syncing to Hubspot', serializedError, {
      ...context,
      duration: Date.now() - startTime,
    });
  }
}
