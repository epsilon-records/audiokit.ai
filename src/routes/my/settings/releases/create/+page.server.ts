import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { pb } from '$lib/pocketbase';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId) {
		throw error(401, 'Unauthorized');
	} else if (!locals.auth?.orgId) {
		redirect(302, '/my/settings/create');
	}
	const releases = await pb.collection('releases').getList(1, 1, {
		filter: `org_id = "${locals.auth.orgId}"`,
	});
	return { releases: releases.items };
}) satisfies PageServerLoad;