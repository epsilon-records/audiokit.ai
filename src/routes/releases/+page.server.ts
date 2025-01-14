import { pb } from '$lib/pocketbase';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    try {
        const releases = await pb.collection('releases').getFullList({
            filter: 'slug != "" && slug != null',
            sort: '-release_date',
            expand: 'tracks.primary_artists'
        });
        
        return {
            releases: releases
        };

    } catch (err) {
        console.error('Error fetching releases:', err);
        return {
            releases: []
        };
    }
}; 