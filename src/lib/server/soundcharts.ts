import { debug, warn } from '../utils/logger.js';
import type { Track, TrackCollectionResponse } from '../types/track.js';
import { error } from '@sveltejs/kit';

/**
 * Get Soundcharts artist ID from Spotify ID
 */
export async function getArtistIdFromSpotify(spotifyId: string): Promise<string | null> {
  const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.9/artist/by-platform/spotify/${spotifyId}`;
  try {
    debug({
      msg: 'Fetching Soundcharts ID',
      url,
      spotifyId,
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      warn({
        msg: 'Failed to fetch Soundcharts ID from Spotify',
        spotifyId,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    debug({
      msg: 'Soundcharts artist response',
      data,
    });

    if (!data.object?.uuid) {
      warn({
        msg: 'No Soundcharts ID found for Spotify',
        spotifyId,
      });
      return null;
    }

    return data.object.uuid;
  } catch (error) {
    debug({
      msg: 'Error fetching Soundcharts ID from Spotify',
      spotifyId,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}

/**
 * Get artist metadata from Soundcharts
 */
export async function getArtistMetadata(uuid: string): Promise<any | null> {
  const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.9/artist/${uuid}`;
  try {
    debug({
      msg: 'Fetching Soundcharts artist metadata',
      url,
      uuid,
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      warn({
        msg: 'Failed to fetch Soundcharts artist metadata',
        uuid,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    debug({
      msg: 'Soundcharts artist metadata response',
      data,
    });

    return data;
  } catch (error) {
    debug({
      msg: 'Error fetching Soundcharts artist metadata',
      uuid,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}

/**
 * Get artist streaming audience from Soundcharts
 */
export async function getArtistStreamingAudience(
  uuid: string,
  platform: 'spotify' | 'apple_music' | 'deezer'
): Promise<any | null> {
  const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2/artist/${uuid}/streaming/${platform}/listening`;
  try {
    debug({
      msg: 'Fetching Soundcharts streaming audience',
      url,
      uuid,
      platform,
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      warn({
        msg: 'Failed to fetch Soundcharts streaming audience',
        uuid,
        platform,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    debug({
      msg: 'Soundcharts streaming audience response',
      data,
    });

    return data;
  } catch (error) {
    debug({
      msg: 'Error fetching Soundcharts streaming audience',
      uuid,
      platform,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}

/**
 * Get artist audience data from Soundcharts
 */
async function getArtistAudience(uuid: string, platform: string): Promise<any | null> {
  const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2/artist/${uuid}/audience/${platform}`;
  try {
    debug({
      msg: 'Fetching artist audience data',
      url,
      uuid,
      platform,
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      warn({
        msg: 'Failed to fetch artist audience data',
        uuid,
        platform,
        status: response.status,
      });
      return null;
    }

    return await response.json();
  } catch (error) {
    debug({
      msg: 'Error fetching artist audience data',
      uuid,
      platform,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}

interface AudiencePlot {
  timestamp: string;
  followerCount: number;
}

interface AudienceData {
  currentFollowers: number | null;
  historicalData: AudiencePlot[];
}

/**
 * Get aggregated artist stats from Soundcharts
 */
export async function getArtistStats(uuid: string): Promise<{
  metadata: any;
  streaming: any;
  followers: Record<string, number | null>;
} | null> {
  try {
    // Get artist metadata
    const metadata = await getArtistMetadata(uuid);
    if (!metadata) {
      return null;
    }

    // Get streaming data for different platforms
    const platforms = ['spotify', 'apple_music', 'deezer'] as const;
    const streamingPromises = platforms.map((platform) =>
      getArtistStreamingAudience(uuid, platform)
    );

    const streamingResults = await Promise.allSettled(streamingPromises);
    const streaming = streamingResults.reduce(
      (acc, result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          acc[platforms[index]] = result.value;
        }
        return acc;
      },
      {} as Record<string, any>
    );

    // Get audience data for social platforms
    const socialPlatforms = ['spotify', 'instagram', 'twitter', 'facebook', 'youtube'] as const;
    const audiencePromises = socialPlatforms.map((platform) => getArtistAudience(uuid, platform));

    const audienceResults = await Promise.allSettled(audiencePromises);
    const followers = audienceResults.reduce(
      (acc, result, index) => {
        const platform = socialPlatforms[index];

        if (result.status === 'fulfilled' && result.value?.items) {
          const items = result.value.items;
          // Get the most recent item by sorting dates
          const latestItem = [...items].sort(
            (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
          )[0];

          acc[platform] = latestItem?.followerCount ?? null;
        } else {
          acc[platform] = null;
        }
        return acc;
      },
      {} as Record<string, number | null>
    );

    return {
      metadata: metadata.object || {},
      streaming,
      followers,
    };
  } catch (error) {
    debug({
      msg: 'Error fetching Soundcharts artist stats',
      uuid,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}

interface GetArtistTracksOptions {
  offset?: number;
  limit?: number;
  sortBy?:
    | 'name'
    | 'releaseDate'
    | 'spotifyStream'
    | 'shazamCount'
    | 'youtubeViews'
    | 'spotifyPopularity';
  sortOrder?: 'asc' | 'desc';
}

export async function getArtistTracks(
  uuid: string,
  options: GetArtistTracksOptions = {}
): Promise<TrackCollectionResponse | null> {
  const { offset, limit, sortBy, sortOrder } = options;

  const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.21/artist/${uuid}/songs`;

  const params = new URLSearchParams();

  if (offset !== undefined) params.set('offset', String(offset));
  if (limit !== undefined) params.set('limit', String(limit));
  if (sortBy !== undefined) params.set('sortBy', sortBy);
  if (sortOrder !== undefined) params.set('sortOrder', sortOrder);

  try {
    debug({
      msg: 'Fetching artist tracks',
      url,
      uuid,
      params: params.toString(),
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (response.status === 401) {
      throw error(401, 'Unauthorized: You are not logged in');
    }

    if (response.status === 403) {
      throw error(403, 'Forbidden: You are not authorized to perform this operation');
    }

    if (response.status === 404) {
      debug({
        msg: 'Artist not found',
        uuid,
      });
      return null;
    }

    if (!response.ok) {
      throw error(response.status, 'Failed to fetch artist tracks');
    }

    const data = await response.json();

    debug({
      msg: 'Soundcharts artist tracks response',
      data,
    });

    return data as TrackCollectionResponse;
  } catch (err) {
    debug({
      msg: 'Error fetching artist tracks',
      uuid,
      error: err instanceof Error ? err.message : 'Unknown error',
    });
    return null;
  }
}

export async function getTrackMetadata(uuid: string): Promise<Track | null> {
  const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.25/song/${uuid}`;

  try {
    debug({
      msg: 'Fetching track metadata',
      url,
      uuid,
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (response.status === 401) {
      throw error(401, 'Unauthorized: You are not logged in');
    }

    if (response.status === 403) {
      throw error(403, 'Forbidden: This endpoint is not included in your current plan');
    }

    if (response.status === 404) {
      debug({
        msg: 'Track not found',
        uuid,
      });
      return null;
    }

    if (!response.ok) {
      throw error(response.status, 'Failed to fetch track metadata');
    }

    const data = await response.json();

    const track = data.object as Track;

    debug({
      msg: 'Track metadata response',
      data: track,
    });

    return track;
  } catch (err) {
    debug({
      msg: 'Error fetching track metadata',
      uuid,
      error: err instanceof Error ? err.message : 'Unknown error',
    });
    throw err;
  }
}
