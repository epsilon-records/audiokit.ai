import type { Track, TrackCollectionResponse } from '../../types/track.js';
import { error } from '@sveltejs/kit';
import logger from '../../utils/logger.js';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';

/**
 * Get Soundcharts artist ID from Spotify ID
 */
export async function getArtistIdFromSpotify(spotifyId: string): Promise<string | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    spotifyId,
  };

  try {
    logger.info(`🔍 Looking up Soundcharts ID from Spotify`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      logger.error(`❌ Soundcharts credentials not configured`, context);
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.9/artist/by-platform/spotify/${spotifyId}`;
    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn(`⚠️ Failed to fetch Soundcharts ID`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const data = await response.json();
    if (!data.object?.uuid) {
      logger.info(`ℹ️ No Soundcharts ID found`, {
        ...context,
        duration: Date.now() - startTime,
      });
      return null;
    }

    logger.info(`✅ Successfully retrieved Soundcharts ID`, {
      ...context,
      duration: Date.now() - startTime,
    });

    return data.object.uuid;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching Soundcharts ID`, {
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
 * Get artist metadata from Soundcharts
 */
export async function getArtistMetadata(uuid: string): Promise<any | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
  };

  try {
    logger.info(`🔍 Fetching Soundcharts artist metadata`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      logger.error(`❌ Soundcharts credentials not configured`, context);
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.9/artist/${uuid}`;
    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn(`⚠️ Failed to fetch artist metadata`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const data = await response.json();
    logger.info(`✅ Successfully retrieved artist metadata`, {
      ...context,
      availableFields: Object.keys(data.object || {}),
      duration: Date.now() - startTime,
    });

    return data;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching artist metadata`, {
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
 * Get artist streaming audience from Soundcharts
 */
export async function getArtistStreamingAudience(
  uuid: string,
  platform: 'spotify' | 'apple_music' | 'deezer'
): Promise<any | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
    platform,
  };

  try {
    logger.info(`🔍 Fetching Soundcharts streaming audience`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      logger.error(`❌ Soundcharts credentials not configured`, context);
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2/artist/${uuid}/streaming/${platform}/listening`;
    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn(`⚠️ Failed to fetch streaming audience`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const data = await response.json();
    logger.info(`✅ Successfully retrieved streaming audience`, {
      ...context,
      dataPoints: data.items?.length || 0,
      duration: Date.now() - startTime,
    });

    return data;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching streaming audience`, {
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
 * Get artist audience data from Soundcharts
 */
async function getArtistAudience(uuid: string, platform: string): Promise<any | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
    platform,
  };

  try {
    logger.info(`🔍 Fetching artist audience data`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      logger.error(`❌ Soundcharts credentials not configured`, context);
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2/artist/${uuid}/audience/${platform}`;
    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn(`⚠️ Failed to fetch audience data`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const data = await response.json();
    logger.info(`✅ Successfully retrieved audience data`, {
      ...context,
      dataPoints: data.items?.length || 0,
      duration: Date.now() - startTime,
    });

    return data;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching audience data`, {
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
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
  };

  try {
    logger.info(`🔍 Fetching aggregated artist stats`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    // Get artist metadata
    const metadata = await getArtistMetadata(uuid);
    if (!metadata) {
      logger.error(`❌ Failed to fetch artist metadata`, context);
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

    logger.info(`✅ Successfully aggregated artist stats`, {
      ...context,
      metadataAvailable: !!metadata.object,
      streamingPlatforms: Object.keys(streaming),
      socialPlatforms: Object.keys(followers),
      duration: Date.now() - startTime,
    });

    return {
      metadata: metadata.object || {},
      streaming,
      followers,
    };
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching artist stats`, {
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
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
    options,
  };

  try {
    logger.info(`🔍 Fetching artist tracks`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      logger.error(`❌ Soundcharts credentials not configured`, context);
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.21/artist/${uuid}/songs`;
    const params = new URLSearchParams();

    if (offset !== undefined) params.set('offset', String(offset));
    if (limit !== undefined) params.set('limit', String(limit));
    if (sortBy !== undefined) params.set('sortBy', sortBy);
    if (sortOrder !== undefined) params.set('sortOrder', sortOrder);

    const response = await fetch(`${url}?${params}`, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (response.status === 401) {
      logger.error(`❌ Unauthorized: Not logged in`, context);
      throw error(401, 'Unauthorized: You are not logged in');
    }

    if (response.status === 403) {
      logger.error(`❌ Forbidden: Not authorized`, context);
      throw error(403, 'Forbidden: You are not authorized to perform this operation');
    }

    if (response.status === 404) {
      logger.warn(`⚠️ Artist not found`, context);
      return null;
    }

    if (!response.ok) {
      logger.error(`❌ Failed to fetch artist tracks`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
      });
      throw error(response.status, 'Failed to fetch artist tracks');
    }

    const data = await response.json();
    logger.info(`✅ Successfully retrieved artist tracks`, {
      ...context,
      trackCount: data.items?.length || 0,
      duration: Date.now() - startTime,
    });

    return data as TrackCollectionResponse;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching artist tracks`, {
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
    throw err;
  }
}

export async function getTrackMetadata(uuid: string): Promise<Track | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
  };

  try {
    logger.info(`🔍 Fetching track metadata`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      logger.error(`❌ Soundcharts credentials not configured`, context);
      throw new Error('SOUNDCHARTS_APP_ID or SOUNDCHARTS_API_KEY is not set');
    }

    const url = `${process.env.SOUNDCHARTS_API_BASE}/api/v2.25/song/${uuid}`;
    const response = await fetch(url, {
      headers: {
        'x-app-id': process.env.SOUNDCHARTS_APP_ID,
        'x-api-key': process.env.SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (response.status === 401) {
      logger.error(`❌ Unauthorized: Not logged in`, context);
      throw error(401, 'Unauthorized: You are not logged in');
    }

    if (response.status === 403) {
      logger.error(`❌ Forbidden: Not authorized`, context);
      throw error(403, 'Forbidden: This endpoint is not included in your current plan');
    }

    if (response.status === 404) {
      logger.warn(`⚠️ Track not found`, context);
      return null;
    }

    if (!response.ok) {
      logger.error(`❌ Failed to fetch track metadata`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
      });
      throw error(response.status, 'Failed to fetch track metadata');
    }

    const data = await response.json();
    const track = data.object as Track;

    logger.info(`✅ Successfully retrieved track metadata`, {
      ...context,
      trackId: track?.uuid,
      availableFields: Object.keys(track),
      duration: Date.now() - startTime,
    });

    return track;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching track metadata`, {
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
    throw err;
  }
}
