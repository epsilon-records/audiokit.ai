import { PIPEDRIVE_API_KEY } from '$env/static/private';
import type { artistSchema } from '$lib/schemas/artist';
import type { z } from 'zod';
import pino from 'pino';

// Initialize logger with consistent configuration
const logger = pino({
  level: 'debug',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      levelFirst: true,
      translateTime: 'SYS:standard',
    },
  },
});

// Core types for Pipedrive API
type Artist = z.infer<typeof artistSchema>;

interface PipedriveResponse<T> {
  success: boolean;
  data: T;
  additional_data?: {
    pagination?: {
      start: number;
      limit: number;
      more_items_in_collection: boolean;
      next_start?: number;
    };
  };
}

interface PipedrivePerson {
  id: number;
  name: string;
  email: string[];
  phone?: string[];
  org_id?: number;
  visible_to: number;
  marketing_status?: string;
  label_ids?: number[];
  custom_fields: Record<string, { value: string | undefined; currency?: string }>;
}

interface PipedriveOrganization {
  id: number;
  name: string;
  address?: string;
  address_city?: string;
  address_country?: string;
  owner_id: number;
  visible_to: number;
  custom_fields: Record<string, { value: string | undefined; currency?: string }>;
}

// Configuration
const API_BASE = 'https://api.pipedrive.com/v1';
const CUSTOM_FIELDS = ['artist_stage_name', 'spotify_url', 'instagram_url'];

// Field mapping for syncing artist data
const FIELD_MAPPING: Record<string, string> = {
  spotify: 'spotify_url',
  instagram: 'instagram_url',
  facebook: 'facebook_url',
  twitter: 'twitter_url',
  tiktok: 'tiktok_url',
  youtube: 'youtube_url',
};

/**
 * Makes an authenticated request to the Pipedrive API
 */
async function makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = new URL(`${API_BASE}${endpoint}`);
  url.searchParams.append('api_token', PIPEDRIVE_API_KEY);

  const requestId = crypto.randomUUID();

  logger.debug({
    requestId,
    method: options.method || 'GET',
    url: url.toString(),
    msg: 'Making Pipedrive API request',
  });

  try {
    const response = await fetch(url.toString(), {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Unknown error occurred');
    }

    const data = await response.json();
    return data as T;
  } catch (error) {
    logger.error({
      requestId,
      error: error instanceof Error ? error.message : String(error),
      msg: 'Pipedrive API request failed',
    });
    throw error;
  }
}

/**
 * Searches for a person in Pipedrive by their stage name
 */
export async function searchPerson(
  stageName: string
): Promise<PipedriveResponse<PipedrivePerson | null>> {
  const requestId = crypto.randomUUID();

  logger.info({
    requestId,
    stageName,
    msg: 'Searching for Pipedrive contact',
  });

  const encodedName = encodeURIComponent(stageName.trim());
  return makeRequest<PipedriveResponse<PipedrivePerson | null>>(
    `/persons/search?term=${encodedName}&fields=custom_fields&exact_match=true`
  );
}

/**
 * Syncs artist data to Pipedrive
 */
export async function syncToPipedrive(artist: Artist): Promise<void> {
  const requestId = crypto.randomUUID();

  if (!artist.email) {
    logger.warn({
      requestId,
      msg: 'Cannot sync to Pipedrive: artist email is missing',
    });
    return;
  }

  try {
    const existingPerson = await searchPerson(artist.name);

    const personData = {
      name: artist.name,
      email: [artist.email],
      phone: artist.phone ? [artist.phone] : undefined,
      visible_to: 3, // Organization-wide visibility
      custom_fields: Object.entries(FIELD_MAPPING).reduce(
        (acc, [artistKey, pipedriveKey]) => ({
          ...acc,
          [pipedriveKey]: { value: artist[artistKey as keyof Artist] },
        }),
        {}
      ),
    };

    if (existingPerson.data) {
      await makeRequest(`/persons/${existingPerson.data.id}`, {
        method: 'PUT',
        body: JSON.stringify(personData),
      });
      logger.info({
        requestId,
        personId: existingPerson.data.id,
        msg: 'Updated existing Pipedrive contact',
      });
    } else {
      const newPerson = await makeRequest('/persons', {
        method: 'POST',
        body: JSON.stringify(personData),
      });
      logger.info({
        requestId,
        personId: newPerson.data.id,
        msg: 'Created new Pipedrive contact',
      });
    }
  } catch (error) {
    logger.error({
      requestId,
      error: error instanceof Error ? error.message : String(error),
      msg: 'Failed to sync artist to Pipedrive',
    });
    throw error;
  }
}

/**
 * Searches for an organization in Pipedrive
 */
export async function searchOrganization(
  name: string
): Promise<PipedriveResponse<PipedriveOrganization | null>> {
  const requestId = crypto.randomUUID();

  logger.info({
    requestId,
    name,
    msg: 'Searching for Pipedrive organization',
  });

  const encodedName = encodeURIComponent(name.trim());
  return makeRequest<PipedriveResponse<PipedriveOrganization | null>>(
    `/organizations/search?term=${encodedName}&exact_match=true&fields=name,address`
  );
}
