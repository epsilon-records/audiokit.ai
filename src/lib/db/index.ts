import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { PUBLIC_SUPABASE_URL } from '$env/static/public';

// Disable prefetch as it is not supported for "Transaction" pool mode
const client = postgres(PUBLIC_SUPABASE_URL, { prepare: false, ssl: 'require' });
export const db = drizzle({ client });
