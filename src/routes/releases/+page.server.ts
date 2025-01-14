import { pb } from '$lib/pocketbase';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    try {
        const records = await pb.collection('releases').getFullList({
            filter: 'slug != "" && slug != null',
            sort: '-release_date',
            expand: 'tracks.primary_artists'
        });
        
        return {
            releases: records
        };

    } catch (err) {
        console.error('Error fetching releases:', err);
        return {
            releases: []
        };
    }
}; 