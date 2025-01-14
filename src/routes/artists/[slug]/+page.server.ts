import { pb } from '$lib/pocketbase';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    try {
        const artist = await pb.collection('artists').getFirstListItem(`slug = "${params.slug}"`, {
            expand: 'country'
        });

        if (!artist) {
            throw error(404, 'Artist not found');
        }

        return {
            artist: {
                ...artist
            }
        };
    } catch (err: any) {
        throw error(500, 'Error fetching artist');
    }
};