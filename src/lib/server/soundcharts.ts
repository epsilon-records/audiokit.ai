import { SOUNDCHARTS_API_BASE, SOUNDCHARTS_API_KEY, SOUNDCHARTS_APP_ID } from '$env/static/private';
import logger from '$lib/utils/logger';

/**
 * Get Soundcharts artist ID from Spotify ID
 */
export async function getArtistIdFromSpotify(spotifyId: string): Promise<string | null> {
  try {
    const response = await fetch(
      `${SOUNDCHARTS_API_BASE}/api/v2.9/artist/by-platform/spotify/${spotifyId}`,
      {
        headers: {
          'x-app-id': SOUNDCHARTS_APP_ID,
          'x-api-key': SOUNDCHARTS_API_KEY,
          Accept: 'application/json',
        },
      }
    );

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

    if (!data.data.object?.uuid) {
      logger.warn({
        msg: 'No Soundcharts ID found for Spotify',
        spotifyId,
      });
      return null;
    }

    return data.id;
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
 * Get artist statistics from Soundcharts
 */
export async function getArtistStats(soundchartsId: string): Promise<{
  metadata: any;
  streaming: any;
  followers: any;
} | null> {
  try {
    const response = await fetch(
      `${SOUNDCHARTS_API_BASE}/api/v2/artist/${soundchartsId}/current/stats`,
      {
        headers: {
          'x-app-id': SOUNDCHARTS_APP_ID,
          'x-api-key': SOUNDCHARTS_API_KEY,
          Accept: 'application/json',
        },
      }
    );

    if (!response.ok) {
      logger.warn({
        msg: 'Failed to fetch Soundcharts stats',
        soundchartsId,
        status: response.status,
      });
      return null;
    }

    const data = await response.json();

    logger.info({
      msg: 'Soundcharts stats response',
      data,
    });

    return {
      metadata: data.metadata,
      streaming: data.streaming,
      followers: data.followers,
    };
  } catch (error) {
    logger.error({
      msg: 'Error fetching Soundcharts stats',
      soundchartsId,
      error: error instanceof Error ? error.message : 'Unknown error',
    });
    return null;
  }
}
