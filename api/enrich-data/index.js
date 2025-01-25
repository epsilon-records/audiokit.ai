import { enrichData } from './enrich.js';

export async function GET() {
  return await enrichData();
}
