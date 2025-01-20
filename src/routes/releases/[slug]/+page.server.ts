import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  try {
    const release = null;

    if (!release) {
      throw error(404, 'Release not found');
    }

    return {
      release: release,
    };
  } catch (err: any) {
    throw error(500, 'Error fetching release');
  }
};
