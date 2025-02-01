import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { eq } from 'drizzle-orm';

export const load: PageServerLoad = async ({ params }) => {
  try {
    const artistData = await db
      .select()
      .from(artists)
      .where(eq(artists.slug, params.slug))
      .limit(1);

    if (!artistData.length) {
      throw error(404, 'Artist not found');
    }

    return {
      artist: artistData[0],
    };
  } catch (err) {
    throw error(500, 'Error fetching artist');
  }
};
