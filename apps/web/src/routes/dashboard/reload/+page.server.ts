/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { redirectUnauthenticated } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
  redirectUnauthenticated(locals, 307, '/sign-in');
  return {};
}) satisfies PageServerLoad;
