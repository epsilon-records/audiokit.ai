import { enrichData } from '../../src/routes/api/enrich-data/enrich.js';

export async function GET() {
  return await enrichData();
}
