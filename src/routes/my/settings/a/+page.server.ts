import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId) {
		throw error(401, 'Unauthorized');
	} else if (!locals.auth?.orgId) {
		redirect(302, '/my/settings/create');
	}
	return {};
}) satisfies PageServerLoad;