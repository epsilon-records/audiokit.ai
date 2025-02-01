import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { releases } from '$lib/db/schema';
import { desc } from 'drizzle-orm';

export const load: PageServerLoad = async () => {
  try {
    const releaseData = await db.select().from(releases).orderBy(desc(releases.created)).limit(50);

    return {
      releases: releaseData,
    };
  } catch (err) {
    return {
      releases: [],
    };
  }
};
