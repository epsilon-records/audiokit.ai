import { enrichData } from './enrich.ts';

export async function GET() {
  return await enrichData();
}
