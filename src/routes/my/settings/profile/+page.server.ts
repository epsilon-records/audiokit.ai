import { message, superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { pb } from '$lib/pocketbase';
import { artistSchema } from '$lib/schemas/artist';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId || !locals.auth?.orgId) {
        throw error(401, 'Unauthorized');
    }
	const artists = await pb.collection('artists').getList(1, 1, {
		filter: `org_id = "${locals.auth.orgId}" || test_org_id = "${locals.auth.orgId}"`,
		sort: `-org_id = "${locals.auth.orgId}"`
	});
	if (artists.totalItems === 0) {
		throw error(404, 'Profile not found');
	}
	const artist = artists.items[0];
	const form = await superValidate(artist, zod(artistSchema));
	return { form };
}) satisfies PageServerLoad;

export const actions = {
  default: async ({ request }) => {
    const form = await superValidate(request, zod(artistSchema));
    if (!form.valid) {
      return fail(400, { form });
    }

    // TODO: Do something with the validated form.data

    return message(form, 'Form posted successfully!');
  }
};