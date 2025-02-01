import { db } from '$lib/db';
import { releases } from '$lib/db/schema';
import { error } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  try {
    const releaseData = await db
      .select()
      .from(releases)
      .where(eq(releases.slug, params.slug))
      .limit(1);

    if (!releaseData.length) {
      throw error(404, 'Release not found');
    }

    return {
      release: releaseData[0],
    };
  } catch (err) {
    throw error(500, 'Error fetching release');
  }
};
