import { enrichData } from '../../src/lib/server/enrich.js';
import logger from '../../src/lib/utils/logger.js';

export async function GET() {
  const response = await enrichData();
  logger.complete('Data enriched', { response });
  return new Response('OK', { status: 200 });
}
