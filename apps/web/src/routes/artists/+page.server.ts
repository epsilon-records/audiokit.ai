import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { error } from '@sveltejs/kit';
import { and, isNotNull, ne } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

export const load = (async () => {
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
}) satisfies PageServerLoad;
