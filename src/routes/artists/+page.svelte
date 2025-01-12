<script lang="ts">
    import { createQuery } from '@tanstack/svelte-query';
    import { pb } from '$lib/pocketbase';

    const artistsQuery = createQuery({
        queryKey: ['artists'],
        queryFn: async () => {
            const records = await pb.collection('artists').getList(1, 50, {
                headers: {
                    'Authorization': `Bearer ${import.meta.env.VITE_API_TOKEN}`
                }
            });
            return records.items;
        }
    });
</script>

<div class="min-h-screen bg-black text-[#00ff00]">
    <div class="container mx-auto px-4 pt-32 pb-12">
        <h1 class="text-4xl font-bold mb-8 tracking-wider uppercase relative inline-block after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-1/2 after:h-[2px] after:bg-[#00ff00] after:animate-pulse">
            Our Artists
        </h1>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {#if $artistsQuery.isLoading}
                <div class="text-[#ff00ff]">Loading...</div>
            {:else if $artistsQuery.isError}
                <div class="text-[#ff0000]">Error: {$artistsQuery.error.message}</div>
            {:else if $artistsQuery.data}
                {#each $artistsQuery.data as artist (artist.id)}
                    <a 
                        href="/artists/{artist.slug}" 
                        class="block relative group opacity-90 hover:opacity-100 overflow-hidden rounded-none border border-[#00ff00] hover:border-[#ff00ff] transition-colors duration-500"
                    >
                        <img 
                            src={Array.isArray(artist.artist_photo) && artist.artist_photo.length > 0 
                                ? pb.files.getURL(artist, artist.artist_photo[0])
                                : '/default-artist.jpg'} 
                            alt={artist.name}
                            class="w-full h-full object-cover aspect-square transition-all duration-500 group-hover:scale-105 group-hover:opacity-80"
                        />
                        <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500 flex items-end p-6">
                            <span class="text-[#00ff00] text-xl font-light tracking-wider uppercase transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500 group-hover:text-[#ff00ff]">
                                {artist.stage_name}
                            </span>
                        </div>
                    </a>
                {/each}
            {/if}
        </div>
    </div>
</div> 