import { error } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions = {
	updateProfile: async ({ request, locals }) => {
		if (!locals?.user?.id) {
			throw error(401, 'Unauthorized');
		}

		const data = await request.formData();
		const userAvatar = data.get('avatar');

		// Clean up empty avatar
		if (userAvatar instanceof File && userAvatar.size === 0) {
			data.delete('avatar');
		}

		try {
			const { name, avatar } = await locals.pb
				.collection('users')
				.update(locals.user.id, data);

			// Update local user data
			locals.user = {
				...locals.user,
				name,
				avatar
			};

			return {
				success: true,
				data: { name, avatar }
			};
		} catch (err) {
			console.error('Profile update error:', err);
			throw error(400, 'Failed to update profile');
		}
	}
} satisfies Actions;