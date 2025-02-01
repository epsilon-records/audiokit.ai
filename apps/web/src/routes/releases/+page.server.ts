import { db } from '$lib/db';
import { releases } from '$lib/db/schema';
import { desc } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

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
