import { error } from '@sveltejs/kit';
import Bottleneck from 'bottleneck';
import { serializeError } from 'serialize-error';
import type { Track, TrackCollectionResponse } from '../../types/track.js';
import logger from '../../utils/logger.js';

const SOUNDCHARTS_RATE_LIMIT = 5; // 5 requests per second
const SOUNDCHARTS_WINDOW = 1000; // 1 second in milliseconds

const soundchartsLimiter = new Bottleneck({
  minTime: SOUNDCHARTS_WINDOW / SOUNDCHARTS_RATE_LIMIT, // 200ms between requests
  maxConcurrent: 1,
  reservoir: SOUNDCHARTS_RATE_LIMIT,
  reservoirRefreshInterval: SOUNDCHARTS_WINDOW,
  reservoirRefreshAmount: SOUNDCHARTS_RATE_LIMIT,
  trackDoneStatus: true,
});

// Add these at the top of the file
type StreamingPlatform =
  | 'audiomack'
  | 'jiosaavn'
  | 'lastfm'
  | 'pandora'
  | 'spotify'
  | 'tidal'
  | 'yandex'
  | 'youtube-artist';

type SocialPlatform = 'spotify' | 'instagram' | 'twitter' | 'facebook' | 'youtube';

const STREAMING_PLATFORMS: StreamingPlatform[] = [
  'audiomack',
  'jiosaavn',
  'lastfm',
  'pandora',
  'spotify',
  'tidal',
  'yandex',
  'youtube-artist',
];

const SOCIAL_PLATFORMS: SocialPlatform[] = [
  'spotify',
  'instagram',
  'twitter',
  'facebook',
  'youtube',
];

function getSoundchartsConfig() {
  const apiBase = process.env.SOUNDCHARTS_API_BASE;
  const appId = process.env.SOUNDCHARTS_APP_ID;
  const apiKey = process.env.SOUNDCHARTS_API_KEY;

  if (!apiBase || !appId || !apiKey) {
    throw new Error('Soundcharts API configuration missing');
  }

  return {
    apiBase,
    headers: {
      'Content-Type': 'application/json',
      'x-app-id': appId,
      'x-api-key': apiKey,
      Accept: 'application/json',
    },
  };
}

/**
 * Get Soundcharts artist ID from Spotify ID
 */
export const getArtistIdFromSpotify = soundchartsLimiter.wrap(
  async (spotifyId: string): Promise<string | null> => {
    const requestId = crypto.randomUUID();
    const startTime = Date.now();
    const context = {
      spotifyId,
      requestId,
    };

    logger.start(requestId, 'Fetching Soundcharts artist ID from Spotify ID', context);

    try {
      const { apiBase, headers } = getSoundchartsConfig();
      logger.process(requestId, 'Looking up Soundcharts ID from Spotify', {
        ...context,
        metadata: {
          environment: process.env.NODE_ENV,
        },
      });

      const url = `${apiBase}/api/v2.9/artist/by-platform/spotify/${spotifyId}`;
      const response = await fetch(url, { headers });

      if (!response.ok) {
        logger.error(
          requestId,
          'Soundcharts API error',
          new Error(`API Error: ${response.status} ${response.statusText}`),
          {
            url,
            status: response.status,
            statusText: response.statusText,
          }
        );
        return null;
      }

      const data = await response.json();
      logger.success(requestId, 'Successfully retrieved Soundcharts artist ID', {
        soundchartsId: data.object?.uuid,
        duration: Date.now() - startTime,
      });

      return data.object?.uuid || null;
    } catch (err) {
      const serializedError = serializeError(err) as Error;
      logger.error(requestId, 'Error fetching Soundcharts artist ID', serializedError);
      return null;
    }
  }
);

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
    const { apiBase, headers } = getSoundchartsConfig();
    const url = `${apiBase}/api/v2.9/artist/${uuid}`;
    const response = await fetch(url, { headers });

    if (!response.ok) {
      const warningContext = {
        ...context,
        url,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      };
      logger.warning(requestId, 'Failed to fetch artist metadata', warningContext);
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
  platform: StreamingPlatform
): Promise<any | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
    platform,
  };

  // Replace the supportedStreamingPlatforms array with this:
  const supportedStreamingPlatforms = STREAMING_PLATFORMS.map((code) => ({
    name: code
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' '),
    code,
  }));

  // Validate platform
  if (!supportedStreamingPlatforms.some((p) => p.code === platform)) {
    logger.error(requestId, 'Unsupported streaming platform', new Error('Unsupported platform'), {
      platform,
      supportedPlatforms: supportedStreamingPlatforms.map((p) => p.code),
    });
    return null;
  }

  try {
    const { apiBase, headers } = getSoundchartsConfig();
    const url = `${apiBase}/api/v2/artist/${uuid}/streaming/${platform}/listening`;
    const response = await fetch(url, { headers });

    if (!response.ok) {
      // Handle expected 404s for missing streaming accounts
      if (response.status === 404) {
        const data = await response.json();
        if (data.errors?.some((error: any) => error.code === 404)) {
          logger.process(
            requestId,
            'No streaming account found for artist on platform',
            {
              platform,
              duration: Date.now() - startTime,
            },
            context
          );
          return null;
        }
      }

      const warningContext = {
        ...context,
        url,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      };
      logger.warning(requestId, 'Failed to fetch artist streaming audience', warningContext);
      return null;
    }

    const data = await response.json();
    logger.process(
      requestId,
      'Successfully retrieved streaming audience',
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
async function getArtistSocialAudience(
  uuid: string,
  platform: SocialPlatform
): Promise<any | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    uuid,
    platform,
  };

  // Replace the supportedSocialPlatforms array with this:
  const supportedSocialPlatforms = SOCIAL_PLATFORMS.map((code) => ({
    name: code
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' '),
    code,
  }));

  // Validate platform
  if (!supportedSocialPlatforms.some((p) => p.code === platform)) {
    logger.error(requestId, 'Unsupported social platform', new Error('Unsupported platform'), {
      platform,
      supportedPlatforms: supportedSocialPlatforms.map((p) => p.code),
    });
    return null;
  }

  try {
    const { apiBase, headers } = getSoundchartsConfig();
    const url = `${apiBase}/api/v2/artist/${uuid}/audience/${platform}`;
    const response = await fetch(url, { headers });

    if (!response.ok) {
      const warningContext = {
        ...context,
        url,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      };
      logger.warning(requestId, 'Failed to fetch artist social audience', warningContext);
      return null;
    }

    const data = await response.json();
    logger.process(
      requestId,
      'Successfully retrieved audience data',
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
export const getArtistStats = soundchartsLimiter.wrap(
  async (
    uuid: string
  ): Promise<{
    metadata: any;
    streaming: any;
    followers: Record<string, number | null>;
  } | null> => {
    const requestId = crypto.randomUUID();
    const startTime = Date.now();
    const context = {
      uuid,
      requestId,
    };

    logger.start(requestId, 'Fetching Soundcharts artist stats', context);

    try {
      // Get artist metadata
      const metadata = await getArtistMetadata(uuid);
      if (!metadata) {
        logger.warning(requestId, 'No metadata found for artist', context);
        return null;
      }

      // Get streaming data for different platforms
      const streamingPromises = STREAMING_PLATFORMS.map((platform) =>
        getArtistStreamingAudience(uuid, platform)
      );

      const streamingResults = await Promise.allSettled(streamingPromises);
      const streaming = streamingResults.reduce(
        (acc, result, index) => {
          if (result.status === 'fulfilled' && result.value) {
            acc[STREAMING_PLATFORMS[index]] = result.value;
          }
          return acc;
        },
        {} as Record<string, any>
      );

      // Get audience data for social platforms
      const audiencePromises = SOCIAL_PLATFORMS.map((platform) =>
        getArtistSocialAudience(uuid, platform)
      );

      const audienceResults = await Promise.allSettled(audiencePromises);
      const followers = audienceResults.reduce(
        (acc, result, index) => {
          const platform = SOCIAL_PLATFORMS[index];

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

      logger.success(requestId, 'Successfully retrieved Soundcharts artist stats', {
        duration: Date.now() - startTime,
        platforms: Object.keys(streaming),
        socialPlatforms: Object.keys(followers),
      });

      return {
        metadata: metadata.object || {},
        streaming,
        followers,
      };
    } catch (err) {
      const serializedError = serializeError(err) as Error;
      logger.error(requestId, 'Error fetching Soundcharts artist stats', serializedError, {
        ...context,
        duration: Date.now() - startTime,
      });
      return null;
    }
  }
);

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

export const getArtistTracks = soundchartsLimiter.wrap(
  async (
    uuid: string,
    options: GetArtistTracksOptions = {}
  ): Promise<TrackCollectionResponse | null> => {
    const { offset, limit, sortBy, sortOrder } = options;
    const requestId = crypto.randomUUID();
    const startTime = Date.now();
    const context = {
      requestId,
      uuid,
      options,
    };

    try {
      const { apiBase, headers } = getSoundchartsConfig();
      const url = `${apiBase}/api/v2.21/artist/${uuid}/songs`;
      const params = new URLSearchParams();

      if (offset !== undefined) params.set('offset', String(offset));
      if (limit !== undefined) params.set('limit', String(limit));
      if (sortBy !== undefined) params.set('sortBy', sortBy);
      if (sortOrder !== undefined) params.set('sortOrder', sortOrder);

      const fullUrl = `${url}?${params}`;
      const response = await fetch(fullUrl, { headers });

      if (response.status === 401) {
        const authError = new Error('Unauthorized: Not logged in');
        logger.error(requestId, 'Unauthorized: Not logged in', authError, context);
        throw error(401, 'Unauthorized: You are not logged in');
      }

      if (response.status === 403) {
        const forbiddenError = new Error('Forbidden: Not authorized');
        logger.error(requestId, 'Forbidden: Not authorized', forbiddenError, context);
        throw error(403, 'Forbidden: You are not authorized to perform this operation');
      }

      if (response.status === 404) {
        logger.warning(requestId, 'Artist not found', context);
        return null;
      }

      if (!response.ok) {
        const apiError = new Error(`API Error: ${response.status} ${response.statusText}`);
        const errorContext = {
          url: fullUrl,
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
        'Successfully retrieved artist tracks',
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
);

export async function getTrackMetadata(uuid: string): Promise<Track | null> {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    uuid,
    requestId,
  };

  logger.start(requestId, 'Fetching Soundcharts track metadata', context);

  try {
    const { apiBase, headers } = getSoundchartsConfig();
    const url = `${apiBase}/api/v2.25/song/${uuid}`;
    const response = await fetch(url, { headers });

    if (!response.ok) {
      const apiError = new Error(`API Error: ${response.status} ${response.statusText}`);
      logger.error(requestId, 'Soundcharts API error', apiError, {
        url,
        duration: Date.now() - startTime,
      });
      return null;
    }

    const data = await response.json();
    logger.success(requestId, 'Successfully retrieved Soundcharts track metadata', {
      duration: Date.now() - startTime,
    });

    return data.object as Track;
  } catch (err) {
    const serializedError = serializeError(err) as Error;
    logger.error(requestId, 'Error fetching Soundcharts track metadata', serializedError, {
      duration: Date.now() - startTime,
    });
    return null;
  }
}
