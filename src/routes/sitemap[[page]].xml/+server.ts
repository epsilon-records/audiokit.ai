import { PUBLIC_ORIGIN } from '$env/static/public';
import * as sitemap from 'super-sitemap';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ params }) => {
  return await sitemap.response({
    origin: PUBLIC_ORIGIN,
    page: params.page,
    excludeRoutePatterns: [
      '^/dashboard.*', // i.e. routes starting with `/dashboard`
    ],
    defaultChangefreq: 'daily',
    defaultPriority: 0.7,
    sort: 'alpha', // default is false; 'alpha' sorts all paths alphabetically.
  });
};
