import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { pb } from '$lib/pocketbase';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId || !locals.auth?.orgId) {
        throw error(401, 'Unauthorized');
    }
	const releases = await pb.collection('releases').getList(1, 1, {
		filter: `org_id = "${locals.auth.orgId}"`,
	});
	return { releases: releases.items };
}) satisfies PageServerLoad;