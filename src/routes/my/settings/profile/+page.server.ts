import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { error } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { z } from 'zod';
import { pb } from '$lib/pocketbase';

// Artist profile schema with more specific validation
const artistSchema = z.object({
	id: z.string().length(15).regex(/^[a-z0-9]+$/),
	org_id: z.string().optional(),
	stage_name: z.string().min(1),
	legal_name: z.string().min(1),
	slug: z.string().optional(),
	is_signed: z.boolean().optional(),
	email: z.string().email(),
	phone: z.string().optional(),
	birthdate: z.string().optional(), // Date will be handled as string in form
	artist_photos: z.any().optional(), // File handling
	city: z.string().optional(),
	country: z.string().optional(), // Relation ID
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
	
	anr: z.string().optional(), // Relation ID
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
    if (!artists?.items?.length) {
        throw error(404, 'Profile not found');
    }
    const artist = artists.items[0];
    const form = await superValidate(artist, zod(artistSchema));
    return { form };
}) satisfies PageServerLoad;

export const actions = {
	// updateProfile: async ({ request, locals }) => {
	// 	if (!user?.id) {
	// 		throw error(401, 'Unauthorized');
	// 	}

	// 	const form = await superValidate(request, zod(profileSchema));

	// 	if (!form.valid) {
	// 		return { form };
	// 	}

	// 	try {
	// 		const formData = new FormData();
			
	// 		// Process nested objects and flatten them for PocketBase
	// 		const processData = (obj: Record<string, any>, prefix = '') => {
	// 			Object.entries(obj).forEach(([key, value]) => {
	// 				const fieldName = prefix ? `${prefix}_${key}` : key;
					
	// 				if (value && typeof value === 'object' && !(value instanceof File)) {
	// 					processData(value, fieldName);
	// 				} else if (value !== null && value !== undefined && value !== '') {
	// 					formData.append(fieldName, value);
	// 				}
	// 			});
	// 		};

	// 		processData(form.data);

	// 		// Handle avatar upload separately
	// 		const avatar = formData.get('avatar');
	// 		if (avatar instanceof File && avatar.size === 0) {
	// 			formData.delete('avatar');
	// 		}

	// 		// Update user profile
	// 		const updatedUser = await locals.pb
	// 			.collection('users')
	// 			.update(locals.user.id, formData);

	// 		// Update session data
	// 		locals.user = {
	// 			...locals.user,
	// 			...updatedUser
	// 		};

	// 		return {
	// 			form: {
	// 				...form,
	// 				message: { type: 'success', text: 'Profile updated successfully' }
	// 			},
	// 			user: updatedUser
	// 		};

	// 	} catch (err) {
	// 		console.error('Profile update error:', err);
	// 		return {
	// 			form: {
	// 				...form,
	// 				message: { type: 'error', text: 'Failed to update profile' }
	// 			}
	// 		};
	// 	}
	// }
} satisfies Actions;