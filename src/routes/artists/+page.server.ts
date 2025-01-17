import { db } from '$lib/db';
import type { PageServerLoad } from './$types';
import { ne, and, isNotNull } from 'drizzle-orm';
import { artists } from '$lib/db/schema';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async () => {
  try {
    const records = await db
      .select()
      .from(artists)
      .where(and(ne(artists.slug, ''), isNotNull(artists.slug)));
    return {
      artists: records,
    };
  } catch (err) {
    throw error(500, 'Error fetching artists');
  }
};
