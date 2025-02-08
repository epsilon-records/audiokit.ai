/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { requireAuth } from '$lib/server/auth';
import type { LayoutServerLoad } from './$types';

export const load = (async ({ locals }) => {
  const auth = await requireAuth(locals);
  return { auth };
}) satisfies LayoutServerLoad;
