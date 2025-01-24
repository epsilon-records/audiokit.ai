import { HUBSPOT_API_KEY } from '$env/static/private';
import type { artistSchema } from '$lib/schemas/artist';
import type { z } from 'zod';

const HUBSPOT_API_BASE = 'https://api.hubapi.com';

interface HubspotContact {
  properties: {
    email: string;
    phone?: string;
    city?: string;
    country?: string;
    website?: string;
    spotify_url?: string;
    instagram_url?: string;
    facebook_url?: string;
    twitter_url?: string;
    tiktok_url?: string;
    soundcloud_url?: string;
    youtube_url?: string;
  };
}

// Define the type from the Zod schema
type Artist = z.infer<typeof artistSchema>;

/**
 * Fetches a contact from HubSpot by email
 */
export async function getHubspotContact(email: string): Promise<HubspotContact | null> {
  try {
    const response = await fetch(`${HUBSPOT_API_BASE}/crm/v3/objects/contacts/search`, {
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

    if (!response.ok) {
      console.error('HubSpot API error:', await response.text());
      return null;
    }

    const data = await response.json();
    if (!data.results?.length) {
      return null;
    }

    return {
      properties: data.results[0].properties,
    };
  } catch (error) {
    console.error('Error fetching HubSpot contact:', error);
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
          spotify_url: artist.spotify,
          instagram_url: artist.instagram,
          facebook_url: artist.facebook,
          twitter_url: artist.x,
          tiktok_url: artist.tiktok,
          soundcloud_url: artist.soundcloud,
          youtube_url: artist.youtube,
          // Add any additional HubSpot-specific properties
          lifecyclestage: 'artist',
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`HubSpot API error: ${await response.text()}`);
    }
  } catch (error) {
    console.error('Error syncing to HubSpot:', error);
    // Don't throw the error - we don't want to break the main flow if HubSpot sync fails
  }
}
