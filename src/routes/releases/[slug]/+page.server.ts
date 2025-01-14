import { pb } from '$lib/pocketbase';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    try {
        const release = await pb.collection('releases').getFirstListItem(`slug = "${params.slug}"`, {
            expand: 'label,genre,subgenre,tracks.primary_artists'
        });

        if (!release) {
            throw error(404, 'Release not found');
        }
        
       return {
            release: release
        };
    } catch (err: any) {
        throw error(500, 'Error fetching release');
    }
};