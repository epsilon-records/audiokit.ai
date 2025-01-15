import { error } from "@sveltejs/kit";
import { artistSchema } from "$lib/schemas/artist";
import { fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { pb } from '$lib/pocketbase';

export const load = async ({ params }) => {
    const artist = await pb.collection('artists').getOne(params.id);
    if (!artist) return error(404, 'Not found');
    const form = await superValidate(artist,zod(artistSchema));
    return { form };
};

export const actions = {
  default: async ({ request, params }) => {
    const form = await superValidate(request, zod(artistSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    try {
      if (!params.id) {
        return fail(400, { form, error: "Missing artist ID" });
      }

      await pb.collection('artists').update(params.id, form.data);

      return { form, success: true };
    } catch (error) {
      return fail(500, { form, error: "Failed to update artist" });
    }
  }
};
