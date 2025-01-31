import Bottleneck from 'bottleneck';
import { serializeError } from 'serialize-error';
import logger from '../../utils/logger.js';
import { sanitizeUrl } from '../../utils/sanitize.js';

interface HubspotContact {
  id: string;
  properties: Record<string, string>;
}

const HUBSPOT_RATE_LIMIT = 50; // 50 requests per 10 seconds (more conservative)
const HUBSPOT_WINDOW = 10 * 1000; // 10 seconds in milliseconds

const hubspotLimiter = new Bottleneck({
  minTime: HUBSPOT_WINDOW / HUBSPOT_RATE_LIMIT, // 200ms between requests
  maxConcurrent: 1,
  reservoir: HUBSPOT_RATE_LIMIT,
  reservoirRefreshInterval: HUBSPOT_WINDOW,
  reservoirRefreshAmount: HUBSPOT_RATE_LIMIT,
  trackDoneStatus: true,
});

/**
 * Fetches a contact from HubSpot by email
 */
export const getHubspotContact = hubspotLimiter.wrap(
  async (email: string): Promise<HubspotContact | null> => {
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
);

// Wrap the syncToHubspot function with the rate limiter
export const syncToHubspot = hubspotLimiter.wrap(
  async (email: string, artistData: Record<string, string | null>): Promise<void> => {
    const requestId = crypto.randomUUID();
    const startTime = Date.now();

    const context = {
      requestId,
      email,
      metadata: {
        environment: process.env.NODE_ENV,
        hubspotApiKey: process.env.HUBSPOT_API_KEY ? '✅ Configured' : '❌ Missing',
        hubspotApiBase: process.env.HUBSPOT_API_BASE ? '✅ Configured' : '❌ Missing',
      },
    };

    logger.start(requestId, 'Starting Hubspot sync', context);

    try {
      // Add sanitization logic here
      const sanitizedData = Object.fromEntries(
        Object.entries(artistData).map(([key, value]) => {
          if (
            ['website', 'spotify', 'appleMusic', 'soundcloud', 'bandcamp', 'instagram'].includes(
              key
            )
          ) {
            return [key, value ? sanitizeUrl(value) : null];
          }
          return [key, value];
        })
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
        throw new Error(`Search failed: ${searchResponse.statusText}`);
      }

      const searchData = await searchResponse.json();
      const contactId = searchData.results?.[0]?.id;

      const endpoint = contactId
        ? `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts/${contactId}`
        : `${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts`;

      const method = contactId ? 'PATCH' : 'POST';

      const payload = {
        properties: {
          email,
          phone: sanitizedData.phone,
          city: sanitizedData.city,
          country: sanitizedData.country,
          biography: sanitizedData.biography,
          website: sanitizedData.website,
          spotify: sanitizedData.spotify,
          instagram: sanitizedData.instagram,
          twitterhandle: sanitizedData.x,
          soundcloud: sanitizedData.soundcloud,
        },
      };

      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.HUBSPOT_API_KEY}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Sync failed: ${response.statusText}`);
      }

      const responseData = await response.json();
      logger.success(requestId, 'Successfully synced artist to Hubspot', {
        contactId: responseData.id,
        operation: contactId ? 'UPDATE' : 'CREATE',
        duration: Date.now() - startTime,
      });
    } catch (err) {
      const serializedError = serializeError(err) as Error;
      logger.error(requestId, 'Error syncing to Hubspot', serializedError, {
        ...context,
        duration: Date.now() - startTime,
      });
      throw err;
    }
  }
);

export const getHubspotData = hubspotLimiter.wrap(
  async (
    email: string
  ): Promise<{
    id: string;
    properties: Record<string, string | null>;
  }> => {
    const response = await fetch(`${process.env.HUBSPOT_API_BASE}/crm/v3/objects/contacts/search`, {
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
        properties: [
          'email',
          'firstname',
          'lastname',
          'website',
          'spotify',
          'apple_music',
          'soundcloud',
          'bandcamp',
          'instagram',
          'phone',
          'city',
          'country',
          'biography',
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(`Hubspot API error: ${response.statusText}`);
    }

    const data = await response.json();
    if (data.results.length === 0) {
      throw new Error('Artist not found in Hubspot');
    }

    return {
      id: data.results[0].id,
      properties: data.results[0].properties,
    };
  }
);
