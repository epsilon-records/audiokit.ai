import { pb } from '$lib/pocketbase';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    try {
        const records = await pb.collection('releases').getList(1, 1, {
            filter: `slug = "${params.slug}"`,
            expand: 'artist'
        });

        if (records.items.length === 0) {
            throw error(404, 'Release not found');
        }

        const release = records.items[0];
        return {
            release: {
                ...release,
                artist: release.expand?.artist
            }
        };
    } catch (err) {
        throw error(500, 'Error fetching release');
    }
}; 