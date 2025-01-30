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
    spotifyId,
    requestId,
  };

  logger.start(requestId, 'Fetching Soundcharts artist ID from Spotify ID', context);

  try {
    logger.process(requestId, 'Looking up Soundcharts ID from Spotify', {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
        soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
        soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.SOUNDCHARTS_API_BASE || !process.env.SOUNDCHARTS_API_KEY) {
      throw new Error('Soundcharts API configuration missing');
    }

    const response = await fetch(
      `${process.env.SOUNDCHARTS_API_BASE}/artists/spotify/${spotifyId}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.SOUNDCHARTS_API_KEY}`,
        },
      }
    );

    if (!response.ok) {
      logger.error(
        requestId,
        'Soundcharts API error',
        new Error(`API Error: ${response.status} ${response.statusText}`)
      );
      return null;
    }

    const data = await response.json();
    logger.success(requestId, 'Successfully retrieved Soundcharts artist ID', {
      soundchartsId: data.id,
      duration: Date.now() - startTime,
    });

    return data.id;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching Soundcharts artist ID', serializedError);
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
    logger.process(
      requestId,
      'Fetching Soundcharts artist metadata',
      {
        metadata: {
          environment: process.env.NODE_ENV,
          soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
          soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
          soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
        },
      },
      context
    );

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      const configError = new Error('Configuration Error');
      logger.error(requestId, 'Soundcharts credentials not configured', configError, context);
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
      const warningContext = {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      };
      logger.warning(requestId, '⚠️ Failed to fetch artist metadata', null, warningContext);
      return null;
    }

    const data = await response.json();
    logger.success(requestId, 'Successfully retrieved artist metadata', {
      availableFields: Object.keys(data.object || {}),
      duration: Date.now() - startTime,
    });

    return data;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching artist metadata', serializedError, {
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
    logger.process(
      requestId,
      'Fetching Soundcharts streaming audience',
      {
        metadata: {
          environment: process.env.NODE_ENV,
          soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
          soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
          soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
        },
      },
      context
    );

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      const configError = new Error('Configuration Error');
      logger.error(requestId, 'Soundcharts credentials not configured', configError, context);
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
      const warningContext = {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      };
      logger.warning(requestId, '⚠️ Failed to fetch streaming audience', null, warningContext);
      return null;
    }

    const data = await response.json();
    logger.process(
      requestId,
      '✅ Successfully retrieved streaming audience',
      {
        dataPoints: data.items?.length || 0,
        duration: Date.now() - startTime,
      },
      context
    );

    return data;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching streaming audience', serializedError, {
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
    logger.process(
      requestId,
      '🔍 Fetching artist audience data',
      {
        metadata: {
          environment: process.env.NODE_ENV,
          soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
          soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
          soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
        },
      },
      context
    );

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      const configError = new Error('Configuration Error');
      logger.error(requestId, 'Soundcharts credentials not configured', configError, context);
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
      const warningContext = {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      };
      logger.warning(requestId, '⚠️ Failed to fetch audience data', null, warningContext);
      return null;
    }

    const data = await response.json();
    logger.process(
      requestId,
      '✅ Successfully retrieved audience data',
      {
        dataPoints: data.items?.length || 0,
        duration: Date.now() - startTime,
      },
      context
    );

    return data;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching audience data', serializedError, {
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
    uuid,
    requestId,
  };

  logger.start(requestId, 'Fetching Soundcharts artist stats', context);

  try {
    const response = await fetch(`${process.env.SOUNDCHARTS_API_BASE}/artists/${uuid}/stats`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.SOUNDCHARTS_API_KEY}`,
      },
    });

    if (!response.ok) {
      logger.error(
        requestId,
        'Soundcharts API error',
        new Error(`API Error: ${response.status} ${response.statusText}`),
        {
          status: response.status,
          statusText: response.statusText,
          ...context,
        }
      );
      return null;
    }

    const data = await response.json();
    logger.success(requestId, 'Successfully retrieved Soundcharts artist stats', {
      duration: Date.now() - startTime,
    });

    return data;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching Soundcharts artist stats', serializedError, {
      ...context,
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
    logger.process(
      requestId,
      '🔍 Fetching artist tracks',
      {
        metadata: {
          environment: process.env.NODE_ENV,
          soundchartsApiBase: process.env.SOUNDCHARTS_API_BASE ? '✅ Configured' : '❌ Missing',
          soundchartsAppId: process.env.SOUNDCHARTS_APP_ID ? '✅ Configured' : '❌ Missing',
          soundchartsApiKey: process.env.SOUNDCHARTS_API_KEY ? '✅ Configured' : '❌ Missing',
        },
      },
      context
    );

    if (!process.env.SOUNDCHARTS_APP_ID || !process.env.SOUNDCHARTS_API_KEY) {
      const configError = new Error('Configuration Error');
      logger.error(requestId, 'Soundcharts credentials not configured', configError, context);
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
      const authError = new Error('Unauthorized: Not logged in');
      logger.error(requestId, '❌ Unauthorized: Not logged in', authError, context);
      throw error(401, 'Unauthorized: You are not logged in');
    }

    if (response.status === 403) {
      const forbiddenError = new Error('Forbidden: Not authorized');
      logger.error(requestId, '❌ Forbidden: Not authorized', forbiddenError, context);
      throw error(403, 'Forbidden: You are not authorized to perform this operation');
    }

    if (response.status === 404) {
      logger.warning(requestId, '⚠️ Artist not found', null, context);
      return null;
    }

    if (!response.ok) {
      const apiError = new Error(`API Error: ${response.status} ${response.statusText}`);
      const errorContext = {
        duration: Date.now() - startTime,
        details: {
          status: response.status,
          statusText: response.statusText,
        },
      };
      logger.error(requestId, 'Failed to fetch artist tracks', apiError, errorContext);
      throw error(response.status, 'Failed to fetch artist tracks');
    }

    const data = await response.json();
    logger.process(
      requestId,
      '✅ Successfully retrieved artist tracks',
      {
        trackCount: data.items?.length || 0,
        duration: Date.now() - startTime,
      },
      context
    );

    return data as TrackCollectionResponse;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching artist tracks', serializedError, {
      duration: Date.now() - startTime,
    });
    throw err;
  }
}

export async function getTrackMetadata(uuid: string): Promise<Track | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    uuid,
    requestId,
  };

  logger.start(requestId, 'Fetching Soundcharts track metadata', context);

  try {
    const response = await fetch(`${process.env.SOUNDCHARTS_API_BASE}/tracks/${uuid}`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.SOUNDCHARTS_API_KEY}`,
      },
    });

    if (!response.ok) {
      const apiError = new Error(`API Error: ${response.status} ${response.statusText}`);
      logger.error(requestId, 'Soundcharts API error', apiError, {
        duration: Date.now() - startTime,
      });
      return null;
    }

    const data = await response.json();
    logger.success(requestId, 'Successfully retrieved Soundcharts track metadata', {
      duration: Date.now() - startTime,
    });

    return data as Track;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching Soundcharts track metadata', serializedError, {
      duration: Date.now() - startTime,
    });
    return null;
  }
}
