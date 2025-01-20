import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  try {
    const artist = null;

    if (!artist) {
      throw error(404, 'Artist not found');
    }

    return {
      artist: null,
    };
  } catch (err: any) {
    throw error(500, 'Error fetching artist');
  }
};
