/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { db } from '$lib/db';
import { artists } from '$lib/db/schema';
import { error } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

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
