import { pb } from '$lib/pocketbase';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    try {
        const record = await pb.collection('releases').getFirstListItem(`slug = "${params.slug}"`, {
            expand: 'tracks.primary_artists'
        });

        return record;
    } catch (err: any) {
        if (err.status === 404) {
            throw error(404, 'Release not found');
        }
        throw error(500, 'Error fetching release');
    }
};