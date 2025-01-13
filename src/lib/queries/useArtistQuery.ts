import { createQuery } from '@tanstack/svelte-query';
import { pb } from '$lib/pocketbase';

export function useArtistQuery(slug: string) {
  return createQuery({
    queryKey: ['artist', slug],
    queryFn: async () => {
      const records = await pb.collection('artists').getList(1, 1, {
        filter: `slug = "${slug}"`,
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_API_TOKEN}`
        }
      });
      
      if (records.items.length === 0) {
        throw new Error('Artist not found');
      }
      
      return records.items[0];
    }
  });
} 