import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (!locals.auth?.userId) {
    throw redirect(307, '/sign-in');
  } else if (!locals.auth.orgId) {
    throw redirect(307, '/dashboard/create-artist');
  }

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
    console.error('Error loading analytics:', err);
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
