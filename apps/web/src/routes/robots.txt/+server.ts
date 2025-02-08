/* CONFIDENTIAL AND PROPRIETARY
 * 
 * Copyright (c) 2025 AudioKit.ai. All rights reserved.
 * 
 * This software is confidential and proprietary.
 */

* 
 * This software is confidential and proprietary.
 */

import { PUBLIC_ORIGIN } from '$env/static/public';

export const prerender = true;

export async function GET(): Promise<Response> {
  // prettier-ignore
  const body = [
    'User-agent: *',
    'Allow: /',
    '',
    `Sitemap: ${PUBLIC_ORIGIN}/sitemap.xml`
  ].join('\n').trim();

  const headers = {
    'Content-Type': 'text/plain',
  };

  return new Response(body, { headers });
}
