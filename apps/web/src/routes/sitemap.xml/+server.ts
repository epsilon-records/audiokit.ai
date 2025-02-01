import type { RequestHandler } from '@sveltejs/kit';
import * as sitemap from 'super-sitemap';
import { PUBLIC_ORIGIN } from '$env/static/public';

export const prerender = true; // optional

export const GET: RequestHandler = async () => {
  return await sitemap.response({
    origin: PUBLIC_ORIGIN,
    excludeRoutePatterns: [
      '^/dashboard.*', // i.e. routes starting with `/dashboard`
      '^/artists.*',
      '^/releases.*',
    ],
    defaultChangefreq: 'daily',
    defaultPriority: 0.7,
    sort: 'alpha', // default is false; 'alpha' sorts all paths alphabetically.
  });
};
