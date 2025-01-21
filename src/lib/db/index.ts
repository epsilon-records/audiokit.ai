import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { SUPABASE_DATABASE_URL } from '$env/static/private';

// Disable prefetch as it is not supported for "Transaction" pool mode
const client = postgres(SUPABASE_DATABASE_URL, { prepare: false, ssl: 'require' });
export const db = drizzle({ client });
