import { db } from '$lib/db';
import type { PageServerLoad } from './$types';
import { desc, eq } from 'drizzle-orm';

export const load: PageServerLoad = async ({ locals }) => {
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
