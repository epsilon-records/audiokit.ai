import { redirect } from '@sveltejs/kit';
import { requireAuth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  requireAuth(locals);

  try {
    return {
      streaming: null,
      social: null,
      revenue: null,
      dateRange: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date(),
      },
    };
  } catch (err) {
    return {
      streaming: [],
      social: [],
      revenue: [],
      dateRange: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date(),
      },
    };
  }
};
