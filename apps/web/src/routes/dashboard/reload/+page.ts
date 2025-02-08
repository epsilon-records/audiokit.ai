/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { invalidateAll } from '$app/navigation';
import logger from '$lib/utils/logger';
import { redirect } from '@sveltejs/kit';

export const load = async () => {
  logger.debug({
    msg: 'Reloading dashboard',
  });
  await invalidateAll();
  throw redirect(307, '/dashboard');
};
