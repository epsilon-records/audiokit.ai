import Bottleneck from 'bottleneck';
import { createCache } from '../../utils/cache.js';
import logger from '../../utils/logger.js';

const MUSICFETCH_RATE_LIMIT = 5; // Increased to 5 requests per second
const MUSICFETCH_WINDOW = 1000; // 1 second window
const MUSICFETCH_MAX_CONCURRENT = 3; // Increased to 3 concurrent requests

const musicfetchLimiter = new Bottleneck({
  minTime: 200, // 200ms between requests (5 requests per second)
  maxConcurrent: MUSICFETCH_MAX_CONCURRENT,
  reservoir: MUSICFETCH_RATE_LIMIT,
  reservoirRefreshInterval: MUSICFETCH_WINDOW,
  reservoirRefreshAmount: MUSICFETCH_RATE_LIMIT,
  trackDoneStatus: true,
});

const musicfetchCache = createCache<Record<string, any>>('musicfetch', {
  ttl: 60 * 1000, // 1 minute
  maxSize: 1000, // Max 1000 cached items
});

class RateLimitError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RateLimitError';
  }
}

function getMusicfetchConfig() {
  const apiBase = process.env.MUSICFETCH_API_BASE;
  const token = process.env.MUSICFETCH_TOKEN;

  if (!apiBase || !token) {
    throw new Error('Musicfetch API configuration missing');
  }

  return {
    apiBase,
    headers: {
      'x-musicfetch-token': token,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  };
}

export const getMusicfetchData = musicfetchLimiter.wrap(
  async (spotifyUrl: string, services: string[]) => {
    const requestId = crypto.randomUUID();
    const startTime = Date.now();

    try {
      const cacheKey = `${spotifyUrl}:${services.join(',')}`;

      const cached = musicfetchCache.get(cacheKey);
      if (cached) {
        logger.success(requestId, 'Returning cached Musicfetch data', undefined, {
          cacheHit: true,
          duration: Date.now() - startTime,
        });
        return cached;
      }

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
        return;
      }

      // Validate Spotify URL format
      const spotifyUrlPattern =
        /^https:\/\/open\.spotify\.com\/(track|album|artist)\/[a-zA-Z0-9]+(\?.*)?$/;
      if (!spotifyUrlPattern.test(spotifyUrl)) {
        logger.error(
          requestId,
          'Invalid Spotify URL format',
          new Error(`Invalid Spotify URL: ${spotifyUrl}`)
        );
        return;
      }

      // Validate services array
      if (!Array.isArray(services) || services.length === 0) {
        logger.error(
          requestId,
          'Invalid services array',
          new Error('Services must be a non-empty array')
        );
        return;
      }

      const { apiBase, headers } = getMusicfetchConfig();
      const apiUrl = new URL(`${apiBase}/url`);
      apiUrl.searchParams.set('url', spotifyUrl);
      apiUrl.searchParams.set('services', services.join(','));

      const response = await fetch(apiUrl.toString(), { headers });

      if (!response.ok) {
        const errorText = await response.text();
        const isRateLimitError = response.status === 429;

        if (isRateLimitError) {
          logger.warning(requestId, 'Musicfetch API rate limit exceeded', {
            status: response.status,
            statusText: response.statusText,
            errorText,
            duration: Date.now() - startTime,
            spotifyUrl,
            services,
          });
          // Continue processing by throwing the error
          throw new RateLimitError(`Rate limit exceeded for ${spotifyUrl}: ${errorText}`);
        } else {
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
          return;
        }
      }

      const data = await response.json();

      musicfetchCache.set(cacheKey, data.result.services);

      logger.success(requestId, 'Successfully retrieved Musicfetch data', undefined, {
        availableServices: Object.keys(data.result.services),
        duration: Date.now() - startTime,
        cacheHit: false,
      });

      return data.result.services;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      // Check if it's a RateLimitError instance
      if (!(error instanceof RateLimitError)) {
        logger.error(requestId, 'Error fetching Musicfetch data', error, {
          duration: Date.now() - startTime,
        });
      }
      return;
    }
  }
);
