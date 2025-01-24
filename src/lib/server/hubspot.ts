import { HUBSPOT_API_KEY } from '$env/static/private';
import type { artistSchema } from '$lib/schemas/artist';
import type { z } from 'zod';
import { info } from '$lib/utils/logger';
import { HUBSPOT_API_BASE, HUBSPOT_LIFECYCLE_STAGE_ARTIST } from '$env/static/private';

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
  try {
    // First search for the contact by email
    const searchResponse = await fetch(`${HUBSPOT_API_BASE}/crm/v3/objects/contacts/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${HUBSPOT_API_KEY}`,
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
    });

    if (!searchResponse.ok) {
      info({
        msg: 'HubSpot API error',
        searchResponse,
      });
      return null;
    }

    const searchData = await searchResponse.json();
    info({
      msg: 'HubSpot search response',
      searchData,
    });

    if (!searchData.results?.length) {
      return null;
    }

    // Get the contact ID from the search results
    const contactId = searchData.results[0].id;

    // Make a second request to get all properties
    const detailResponse = await fetch(
      `${HUBSPOT_API_BASE}/crm/v3/objects/contacts/${contactId}?properties=firstname,lastname,email,phone,city,country,website,spotify,instagram,facebook,x,tiktok,soundcloud,youtube`,
      {
        headers: {
          Authorization: `Bearer ${HUBSPOT_API_KEY}`,
        },
      }
    );

    if (!detailResponse.ok) {
      info({
        msg: 'HubSpot API error fetching details',
        detailResponse,
      });
      return null;
    }

    const detailData = await detailResponse.json();
    info({
      msg: 'HubSpot detail response',
      detailData,
    });

    return {
      id: contactId,
      properties: detailData.properties,
    };
  } catch (error) {
    info({
      msg: 'Error fetching HubSpot contact',
      error,
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

  try {
    // First try to find existing contact
    const existingContact = await getHubspotContact(artist.email);

    info({
      msg: 'Existing HubSpot contact',
      existingContact,
    });

    const endpoint = existingContact
      ? `${HUBSPOT_API_BASE}/crm/v3/objects/contacts/${existingContact.id}`
      : `${HUBSPOT_API_BASE}/crm/v3/objects/contacts`;

    const method = existingContact ? 'PATCH' : 'POST';

    const payload = {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${HUBSPOT_API_KEY}`,
      },
      body: {
        properties: {
          email: artist.email,
          phone: artist.phone,
          city: artist.city,
          country: artist.country,
          website: artist.website,
          spotify: artist.spotify,
          instagram: artist.instagram,
          facebook: artist.facebook,
          x: artist.x,
          tiktok: artist.tiktok,
          soundcloud: artist.soundcloud,
          youtube: artist.youtube,
          lifecyclestage: HUBSPOT_LIFECYCLE_STAGE_ARTIST,
        },
      },
    };
    info({
      msg: 'HubSpot sync payload',
      endpoint,
      payload,
    });

    const response = await fetch(endpoint, {
      method: payload.method,
      headers: payload.headers,
      body: JSON.stringify(payload.body),
    });

    info({
      msg: 'HubSpot sync response status',
      status: response.status,
      statusText: response.statusText,
    });

    if (!response.ok) {
      const errorText = await response.text();
      info({
        msg: 'HubSpot API error',
        errorText,
      });
      throw new Error(`HubSpot API error: ${errorText}`);
    }

    let responseData;
    try {
      responseData = await response.json();
      info({
        msg: 'HubSpot sync response data',
        responseData,
      });
    } catch (parseError) {
      info({
        msg: 'Error parsing HubSpot response JSON',
        parseError,
      });
      // Handle parsing error, possibly by reading response as text
      const responseText = await response.text();
      info({
        msg: 'HubSpot response text',
        responseText,
      });
    }
  } catch (error) {
    info({
      msg: 'Error syncing to HubSpot',
      error,
    });
    // Don't throw the error - we don't want to break the main flow if HubSpot sync fails
  }
}
