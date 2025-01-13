import { pb } from '$lib/pocketbase';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    try {
        const records = await pb.collection('artists').getList(1, 50);
        
        return {
            artists: records.items
        };
    } catch (err) {
        console.error('Error fetching artists:', err);
        return {
            artists: []
        };
    }
}; 