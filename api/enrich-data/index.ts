import { enrichData } from './enrich.cjs';

export async function GET() {
  return await enrichData();
}
