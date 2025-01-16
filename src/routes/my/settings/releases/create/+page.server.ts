import { error, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { releaseSchema } from '$lib/schemas/release';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId) {
		return redirect(307, '/sign-in');
	} else if (!locals.auth?.orgId) {
		return redirect(302, '/my/settings/create');
	}
	const form = await superValidate(zod(releaseSchema));
	return { form };
}) satisfies PageServerLoad;