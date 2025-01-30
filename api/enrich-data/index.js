import { enrichData } from '../../src/lib/server/enrich.js';

export async function GET() {
  const response = await enrichData();
  return response;
}
