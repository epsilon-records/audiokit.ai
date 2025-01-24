import { SOUNDCHARTS_API_BASE, SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';
import logger from '$lib/utils/logger';

/**
 * Get Soundcharts artist ID from Spotify ID
 */
export async function getArtistIdFromSpotify(spotifyId: string): Promise<string | null> {
  const url = `${SOUNDCHARTS_API_BASE}/api/v2.9/artist/by-platform/spotify/${spotifyId}`;
  try {
    logger.info({
      msg: 'Fetching Soundcharts ID',
      url,
      spotifyId,
    });

    const response = await fetch(url, {
      headers: {
        'x-app-id': SOUNDCHARTS_APP_ID,
        'x-api-key': SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn({
        msg: 'Failed to fetch Soundcharts ID from Spotify',
        spotifyId,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    logger.info({
      msg: 'Soundcharts artist response',
      data,
    });

    if (!data.object?.uuid) {
      logger.warn({
        msg: 'No Soundcharts ID found for Spotify',
        spotifyId,
      });
      return null;
    }

    return data.object.uuid;
  } catch (error) {
    logger.error({
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
  const url = `${SOUNDCHARTS_API_BASE}/api/v2.9/artist/${uuid}`;
  try {
    logger.info({
      msg: 'Fetching Soundcharts artist metadata',
      url,
      uuid,
    });

    const response = await fetch(url, {
      headers: {
        'x-app-id': SOUNDCHARTS_APP_ID,
        'x-api-key': SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn({
        msg: 'Failed to fetch Soundcharts artist metadata',
        uuid,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    logger.info({
      msg: 'Soundcharts artist metadata response',
      data,
    });

    return data;
  } catch (error) {
    logger.error({
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
  const url = `${SOUNDCHARTS_API_BASE}/api/v2/artist/${uuid}/streaming/${platform}/listening`;
  try {
    logger.info({
      msg: 'Fetching Soundcharts streaming audience',
      url,
      uuid,
      platform,
    });

    const response = await fetch(url, {
      headers: {
        'x-app-id': SOUNDCHARTS_APP_ID,
        'x-api-key': SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn({
        msg: 'Failed to fetch Soundcharts streaming audience',
        uuid,
        platform,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    logger.info({
      msg: 'Soundcharts streaming audience response',
      data,
    });

    return data;
  } catch (error) {
    logger.error({
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
  const url = `${SOUNDCHARTS_API_BASE}/api/v2/artist/${uuid}/audience/${platform}`;
  try {
    logger.info({
      msg: 'Fetching artist audience data',
      url,
      uuid,
      platform,
    });

    const response = await fetch(url, {
      headers: {
        'x-app-id': SOUNDCHARTS_APP_ID,
        'x-api-key': SOUNDCHARTS_API_KEY,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      logger.warn({
        msg: 'Failed to fetch artist audience data',
        uuid,
        platform,
        status: response.status,
      });
      return null;
    }

    return await response.json();
  } catch (error) {
    logger.error({
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
    logger.error({
      msg: 'Error fetching Soundcharts artist stats',
      uuid,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}
