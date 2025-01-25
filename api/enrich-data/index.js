import { enrichData } from '../../src/lib/server/enrich.js';

export async function GET() {
  return await enrichData();
}
