import { HUBSPOT_API_KEY } from '$env/static/private';
import type { artistSchema } from '$lib/schemas/artist';
import type { z } from 'zod';
import { info } from '$lib/utils/logger';
import { HUBSPOT_API_BASE } from '$env/static/private';

interface HubspotContact {
  properties: {
    email: string;
    phone?: string;
    city?: string;
    country?: string;
    website?: string;
    spotify?: string;
    instagram?: string;
    facebook?: string;
    twitter?: string;
    tiktok?: string;
    soundcloud?: string;
    youtube?: string;
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
      `${HUBSPOT_API_BASE}/crm/v3/objects/contacts/${contactId}?properties=email,phone,city,country,website,spotify,instagram,facebook,twitter,tiktok,soundcloud,youtube`,
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
    const endpoint = existingContact
      ? `${HUBSPOT_API_BASE}/crm/v3/objects/contacts/${existingContact.properties.email}`
      : `${HUBSPOT_API_BASE}/crm/v3/objects/contacts`;

    const method = existingContact ? 'PATCH' : 'POST';

    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${HUBSPOT_API_KEY}`,
      },
      body: JSON.stringify({
        properties: {
          email: artist.email,
          phone: artist.phone,
          city: artist.city,
          country: artist.country,
          website: artist.website,
          spotify: artist.spotify,
          instagram: artist.instagram,
          facebook: artist.facebook,
          twitter: artist.x,
          tiktok: artist.tiktok,
          soundcloud: artist.soundcloud,
          youtube: artist.youtube,
          lifecyclestage: 'artist',
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`HubSpot API error: ${await response.text()}`);
    }

    const responseData = await response.json();
    info({
      msg: 'HubSpot sync response',
      responseData,
    });
  } catch (error) {
    info({
      msg: 'Error syncing to HubSpot',
      error,
    });
    // Don't throw the error - we don't want to break the main flow if HubSpot sync fails
  }
}
