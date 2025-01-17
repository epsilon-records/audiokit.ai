import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (() => {
  throw error(500, 'Internal Error');
}) satisfies PageServerLoad;
