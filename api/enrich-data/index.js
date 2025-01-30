import { enrichData } from '../../src/lib/server/enrich.js';
import logger from '../../src/lib/utils/logger.js';

export async function GET() {
  const requestId = crypto.randomUUID();
  const startTime = Date.now();

  try {
    const response = await enrichData();

    logger.complete(requestId, 'Data enrichment completed', {
      duration: Date.now() - startTime,
      status: 'success',
      response: {
        status: response.status,
        statusText: response.statusText,
        data: await response.json(),
      },
    });

    return new Response('OK', { status: 200 });
  } catch (error) {
    logger.error(requestId, 'Data enrichment failed', error, {
      duration: Date.now() - startTime,
    });
    return new Response('Error', { status: 500 });
  }
}
