import { pb } from '$lib/pocketbase';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    try {
        const records = await pb.collection('artists').getList(1, 1, {
            filter: `slug = "${params.slug}"`,
            expand: 'country',
            headers: {
                'Authorization': `Bearer ${process.env.POCKETBASE_API_TOKEN}`
            }
        });

        if (records.items.length === 0) {
            throw error(404, 'Artist not found');
        }

        const artist = records.items[0];
        return {
            artist: {
                ...artist,
                country: artist.expand?.country?.name || 'Unknown'
            }
        };
    } catch (err) {
        throw error(500, 'Error fetching artist');
    }
}; 