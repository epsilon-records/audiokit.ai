import { message, superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { pb } from '$lib/pocketbase';
import { releaseSchema } from '$lib/schemas/release';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId || !locals.auth?.orgId) {
        throw error(401, 'Unauthorized');
    }
	const releases = await pb.collection('releases').getList(1, 1, {
		filter: `org_id = "${locals.auth.orgId}"`,
	});
	if (releases.totalItems === 0) {
		throw error(404, 'Release not found');
	}
	const release = releases.items[0];
	const form = await superValidate(release, zod(releaseSchema));
	return { form };
}) satisfies PageServerLoad;

export const actions = {
  default: async ({ request }) => {
    const form = await superValidate(request, zod(releaseSchema));
    if (!form.valid) {
      return fail(400, { form });
    }

    // TODO: Do something with the validated form.data

    return message(form, 'Form posted successfully!');
  }
};