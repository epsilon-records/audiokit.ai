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
import { getOrg, getUser, requireAuth } from '$lib/server/auth';
import { error } from '@sveltejs/kit';
import { eq } from 'drizzle-orm';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  if (!auth) {
    throw error(401, 'Unauthorized');
  }

  const user = await getUser(auth.userId);
  if (!user) {
    throw error(404, 'User not found');
  }

  const org = await getOrg(auth.orgId);
  if (!org) {
    throw error(404, 'Organization not found');
  }

  const [artist] = await db.select().from(artists).where(eq(artists.orgId, auth.orgId));

  return {
    auth,
    artist,
  };
}) satisfies PageServerLoad;
