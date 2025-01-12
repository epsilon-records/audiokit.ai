<script lang="ts">
    import { page } from '$app/stores';
    import { createQuery } from '@tanstack/svelte-query';
    import { pb } from '$lib/pocketbase';

    const artistQuery = createQuery({
        queryKey: ['artist', $page.params.slug],
        queryFn: async () => {
            const records = await pb.collection('artists').getList(1, 1, {
                filter: `slug = "${$page.params.slug}"`,
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
</script>

<div class="min-h-screen bg-black text-[#00ff00]">
    <div class="container mx-auto px-4 pt-32 pb-12">
        <a 
            href="/artists" 
            class="inline-flex items-center gap-2 text-[#00ffff] hover:text-[#ff00ff] transition-colors mb-8"
        >
            <span class="text-2xl">←</span>
            <span class="uppercase tracking-wider">Back to Artists</span>
        </a>

        {#if $artistQuery.isLoading}
            <div class="text-[#ff00ff]">Loading...</div>
        {:else if $artistQuery.isError}
            <div class="text-[#ff0000]">Error: {$artistQuery.error.message}</div>
        {:else if $artistQuery.data}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                <!-- Artist Image -->
                <div class="relative aspect-square overflow-hidden border border-[#00ff00]">
                    <img 
                        src={Array.isArray($artistQuery.data.artist_photo) && $artistQuery.data.artist_photo.length > 0 
                            ? pb.files.getURL($artistQuery.data, $artistQuery.data.artist_photo[0])
                            : '/default-artist.jpg'} 
                        alt={$artistQuery.data.stage_name}
                        class="w-full h-full object-cover"
                    />
                </div>

                <!-- Artist Info -->
                <div class="flex flex-col gap-6">
                    <h1 class="text-4xl font-bold tracking-wider uppercase text-[#ff00ff]">
                        {$artistQuery.data.stage_name}
                    </h1>
                    
                    {#if $artistQuery.data.real_name}
                        <div>
                            <h2 class="text-sm text-[#00ffff] uppercase mb-1">Real Name</h2>
                            <p class="text-lg text-[#00ff00]">{$artistQuery.data.real_name}</p>
                        </div>
                    {/if}

                    {#if $artistQuery.data.bio}
                        <div>
                            <h2 class="text-sm text-[#00ffff] uppercase mb-1">Biography</h2>
                            <p class="text-lg leading-relaxed text-[#00ff00]">{$artistQuery.data.bio}</p>
                        </div>
                    {/if}

                    {#if $artistQuery.data.location}
                        <div>
                            <h2 class="text-sm text-[#00ffff] uppercase mb-1">Location</h2>
                            <p class="text-lg text-[#00ff00]">{$artistQuery.data.location}</p>
                        </div>
                    {/if}

                    {#if $artistQuery.data.social_links}
                        <div>
                            <h2 class="text-sm text-[#00ffff] uppercase mb-2">Follow</h2>
                            <div class="flex gap-4">
                                {#each Object.entries($artistQuery.data.social_links) as [platform, url]}
                                    <a 
                                        href={url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        class="text-[#ff00ff] hover:text-[#00ffff] transition-colors"
                                    >
                                        {platform}
                                    </a>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>
            </div>
        {/if}
    </div>
</div> 