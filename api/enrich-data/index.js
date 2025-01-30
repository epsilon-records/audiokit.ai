import { enrichData } from '../../src/lib/server/enrich.js';

export async function GET() {
  const response = await enrichData();
  response.status = 200;
  return response;
}
