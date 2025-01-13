import { pb } from '$lib/pocketbase';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    try {
        const records = await pb.collection('releases').getList(1, 50, {
            sort: '-release_date',
            expand: 'artist',
        });
        
        return {
            releases: records.items
        };
    } catch (err) {
        console.error('Error fetching releases:', err);
        return {
            releases: []
        };
    }
}; 