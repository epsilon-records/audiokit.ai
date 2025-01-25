import { enrichData } from '../../src/lib/server/enrich.js';

export async function GET() {
  await enrichData();
  return new Response('Data enriched', { status: 200 });
}
