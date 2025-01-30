import { enrichData } from '../../src/lib/server/enrich.js';

export async function GET() {
  const result = await enrichData();
  return new Response(result, { status: 200 });
}
