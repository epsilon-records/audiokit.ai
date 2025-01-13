import { pb } from '$lib/pocketbase';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    try {
        const records = await pb.collection('artists').getFullList({
            filter: 'slug != "" && slug != null'
        });

        return {
            artists: records
        };
    } catch (err) {
        console.error('Error fetching artists:', err);
        return {
            artists: []
        };
    }
};