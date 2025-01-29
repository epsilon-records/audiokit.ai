import logger from '../../utils/logger.js';
import { serializeError } from 'serialize-error';
import { inspect } from 'util';

export async function getMusicfetchData(spotifyUrl: string, services: string[]) {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();
  const context = {
    requestId,
    spotifyUrl,
    requestedServices: services,
  };

  try {
    logger.info(`🔍 Starting Musicfetch API request`, {
      ...context,
      metadata: {
        environment: process.env.NODE_ENV,
        musicfetchToken: process.env.MUSICFETCH_TOKEN ? '✅ Configured' : '❌ Missing',
        musicfetchApiBase: process.env.MUSICFETCH_API_BASE ? '✅ Configured' : '❌ Missing',
      },
    });

    if (!process.env.MUSICFETCH_TOKEN) {
      logger.error(`❌ Musicfetch token not configured`, context);
      throw new Error('MUSICFETCH_TOKEN is not set');
    }

    const response: Response = await fetch(
      `${process.env.MUSICFETCH_API_BASE}/url?url=${encodeURIComponent(spotifyUrl)}&services=${services.join(',')}`,
      {
        headers: {
          'x-musicfetch-token': process.env.MUSICFETCH_TOKEN,
        },
      }
    );

    if (!response.ok) {
      logger.error(`❌ Musicfetch API error`, {
        ...context,
        status: response.status,
        statusText: response.statusText,
        duration: Date.now() - startTime,
      });
      throw new Error(`Musicfetch request failed with status ${response.status}`);
    }

    const data = await response.json();
    logger.info(`✅ Successfully retrieved Musicfetch data`, {
      ...context,
      availableServices: Object.keys(data.result.services),
      duration: Date.now() - startTime,
    });

    return data.result.services;
  } catch (err) {
    const serializedError = serializeError(err);
    logger.error(`💥 Error fetching Musicfetch data`, {
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
