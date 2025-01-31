import Bottleneck from 'bottleneck';
import logger from '../../utils/logger.js';

const MUSICFETCH_RATE_LIMIT = 10; // 10 requests per second
const MUSICFETCH_WINDOW = 1000; // 1 second in milliseconds

const musicfetchLimiter = new Bottleneck({
  minTime: MUSICFETCH_WINDOW / MUSICFETCH_RATE_LIMIT, // 100ms between requests
  maxConcurrent: 1,
  reservoir: MUSICFETCH_RATE_LIMIT,
  reservoirRefreshInterval: MUSICFETCH_WINDOW,
  reservoirRefreshAmount: MUSICFETCH_RATE_LIMIT,
  trackDoneStatus: true,
});

export const getMusicfetchData = musicfetchLimiter.wrap(
  async (spotifyUrl: string, services: string[]) => {
    const requestId = crypto.randomUUID();
    const startTime = Date.now();
    const context = {
      spotifyUrl,
      requestedServices: services,
    };

    try {
      logger.start(requestId, 'Starting Musicfetch API request', {
        metadata: {
          environment: process.env.NODE_ENV,
          musicfetchToken: process.env.MUSICFETCH_TOKEN ? '✅ Configured' : '❌ Missing',
          musicfetchApiBase: process.env.MUSICFETCH_API_BASE ? '✅ Configured' : '❌ Missing',
        },
      });

      if (!process.env.MUSICFETCH_TOKEN) {
        logger.error(
          requestId,
          'Musicfetch token not configured',
          new Error('MUSICFETCH_TOKEN is not set')
        );
        throw new Error('MUSICFETCH_TOKEN is not set');
      }

      const response = await fetch(
        `${process.env.MUSICFETCH_API_BASE}/url?url=${encodeURIComponent(spotifyUrl)}&services=${services.join(',')}`,
        {
          headers: {
            'x-musicfetch-token': process.env.MUSICFETCH_TOKEN,
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        logger.error(
          requestId,
          'Musicfetch API error',
          new Error(`Musicfetch request failed with status ${response.status}: ${errorText}`),
          {
            status: response.status,
            statusText: response.statusText,
            errorText,
            duration: Date.now() - startTime,
          }
        );
        throw new Error(`Musicfetch request failed with status ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      logger.success(requestId, 'Successfully retrieved Musicfetch data', undefined, {
        availableServices: Object.keys(data.result.services),
        duration: Date.now() - startTime,
      });

      return data.result.services;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error(requestId, 'Error fetching Musicfetch data', error, {
        duration: Date.now() - startTime,
      });
      throw error;
    }
  }
);
