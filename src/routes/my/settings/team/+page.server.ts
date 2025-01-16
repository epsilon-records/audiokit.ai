import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId) {
		return redirect(307, '/sign-in');
	} else if (!locals.auth?.orgId) {
		return redirect(302, '/my/settings/create');
	}
	return {};
}) satisfies PageServerLoad;