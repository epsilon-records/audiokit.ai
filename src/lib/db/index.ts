import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import logger from '../utils/logger';

// Disable prefetch as it is not supported for "Transaction" pool mode
if (!process.env.DATABASE_URL) {
  logger.warning(crypto.randomUUID(), 'DATABASE_URL is not set');
}
const client = postgres(process.env.DATABASE_URL ?? '', { prepare: false, ssl: 'require' });
export const db = drizzle({ client });
