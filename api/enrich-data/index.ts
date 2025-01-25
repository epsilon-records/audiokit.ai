import { enrichData } from './enrich.cjs';

export async function GET() {
  await enrichData();
}
