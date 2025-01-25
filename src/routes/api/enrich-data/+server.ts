import { enrichData } from './enrich.js';
import type { Config } from '@sveltejs/adapter-vercel';

export const config: Config = {
  runtime: 'nodejs20.x',
};

export async function GET() {
  return await enrichData();
}
