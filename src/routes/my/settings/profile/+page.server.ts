import { message, superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail, redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { pb } from '$lib/pocketbase';
import { artistSchema } from '$lib/schemas/artist';

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId) {
		return redirect(307, '/sign-in');
	} else if (!locals.auth?.orgId) {
		return redirect(302, '/my/settings/create');
	}
	const artists = await pb.collection('artists').getList(1, 1, {
		filter: `org_id = "${locals.auth.orgId}"`,
	});
	let artist;
	if (artists.totalItems === 0) {
		artist = await pb.collection('artists').create({
			org_id: locals.auth.orgId
		});
	} else {
		artist = artists.items[0];
	}
	const form = await superValidate(artist, zod(artistSchema));
	return { form };
}) satisfies PageServerLoad;

export const actions = {
  default: async ({ request, locals }) => {
    const form = await superValidate(request, zod(artistSchema));
    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      const artists = await pb.collection('artists').getList(1, 1, {
        filter: `org_id = "${locals.auth?.orgId}"`,
      });
      
      if (artists.totalItems === 0) {
        throw error(404, 'Artist not found');
      }
      await pb.collection('artists').update(artists.items[0].id, form.data);
      return message(form, 'Profile updated successfully!');
    } catch (err) {
      return message(form, 'Failed to update profile. Please try again.', {
        status: 500
      });
    }
  }
};