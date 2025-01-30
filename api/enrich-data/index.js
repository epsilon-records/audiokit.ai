import { enrichData } from '../../src/lib/server/enrich.js';

export async function GET() {
  const result = await enrichData();
  return new Response(JSON.stringify(result), { status: 200 });
}
