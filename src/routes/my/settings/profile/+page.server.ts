import { message, superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { z } from 'zod';
import { pb } from '$lib/pocketbase';

// Artist profile schema with more specific validation
const artistSchema = z.object({
	id: z.string().length(15).regex(/^[a-z0-9]+$/),
	org_id: z.string().optional(),
	stage_name: z.string().min(1),
	legal_name: z.string().min(1),
	is_signed: z.boolean().optional(),
	email: z.string().email(),
	phone: z.string().optional(),
	// birthdate: z.string().optional(), // Date will be handled as string in form
	// artist_photos: z.any().optional(), // File handling
	city: z.string().optional(),
	// country: z.string().optional(), // Relation ID
	biography: z.string().optional(),
	
	// URLs with domain validation where specified
	website: z.string().url().optional().or(z.literal('')),
	spotify: z.string().url().regex(/^https?:\/\/open\.spotify\.com/).optional().or(z.literal('')),
	apple_music: z.string().url().regex(/^https?:\/\/music\.apple\.com/).optional().or(z.literal('')),
	bandcamp: z.string().url().optional().or(z.literal('')),
	mixcloud: z.string().url().regex(/^https?:\/\/mixcloud\.com/).optional().or(z.literal('')),
	snapchat: z.string().url().regex(/^https?:\/\/snapchat\.com/).optional().or(z.literal('')),
	twitch: z.string().url().regex(/^https?:\/\/twitch\.tv/).optional().or(z.literal('')),
	youtube: z.string().url().regex(/^https?:\/\/youtube\.com/).optional().or(z.literal('')),
	instagram: z.string().url().regex(/^https?:\/\/instagram\.com/).optional().or(z.literal('')),
	facebook: z.string().url().regex(/^https?:\/\/facebook\.com/).optional().or(z.literal('')),
	x: z.string().url().regex(/^https?:\/\/(x|twitter)\.com/).optional().or(z.literal('')),
	tiktok: z.string().url().regex(/^https?:\/\/tiktok\.com/).optional().or(z.literal('')),
	soundcloud: z.string().url().regex(/^https?:\/\/soundcloud\.com/).optional().or(z.literal('')),
	songkick: z.string().url().regex(/^https?:\/\/songkick\.com/).optional().or(z.literal('')),
	bandsintown: z.string().url().regex(/^https?:\/\/bandsintown\.com/).optional().or(z.literal('')),
	linkedin: z.string().url().regex(/^https?:\/\/linkedin\.com/).optional().or(z.literal('')),
	
	// anr: z.string().optional(), // Relation ID
	created: z.string().optional(),
	updated: z.string().optional()
});

export const load = (async ({ locals }) => {
	if (!locals.auth?.userId || !locals.auth?.orgId) {
        throw error(401, 'Unauthorized');
    }
	const artists = await pb.collection('artists').getList(1, 1, {
		filter: `org_id = "${locals.auth.orgId}"`,
	});
	if (artists.totalItems === 0) {
		throw error(404, 'Profile not found');
	}
	const artist = structuredClone(artists.items[0]);
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