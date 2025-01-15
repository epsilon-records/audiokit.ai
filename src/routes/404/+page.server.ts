import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (() => {
    throw error(404, 'Page not found');
}) satisfies PageServerLoad; 