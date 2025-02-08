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
