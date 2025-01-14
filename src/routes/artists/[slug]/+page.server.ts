import { pb } from '$lib/pocketbase';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    try {
        const artist = await pb.collection('artists').getFirstListItem(`slug = "${params.slug}"`, {
            expand: 'country'
        });

        return {
            artist: {
                ...artist,
                country: artist.expand?.country?.name || 'Unknown'
            }
        };
    } catch (err: any) {
        if (err.status === 404) {
            throw error(404, 'Artist not found');
        }
        console.log(err);
        throw error(500, 'Error fetching artist');
    }
};