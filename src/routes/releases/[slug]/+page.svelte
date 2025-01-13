<script lang="ts">
    import { pb } from '$lib/pocketbase';
    import { Button } from '$lib/components/ui/button';
    
    let { data } = $props<{ data: { release: any } }>();

    const coverArtUrl = $derived(
        data.release.cover_artwork?.[0] 
            ? pb.files.getURL(data.release, data.release.cover_artwork[0])
            : '/default-release.jpg'
    );
</script>

<div class="min-h-screen bg-black text-[#00ff00]">
    <div class="container mx-auto px-4 pt-32 pb-12">
        <a 
            href="/releases" 
            class="inline-flex items-center gap-2 text-[#00ffff] hover:text-[#ff00ff] transition-colors mb-8"
        >
            <span class="text-2xl">←</span>
            <span class="uppercase tracking-wider">Back to Releases</span>
        </a>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div class="aspect-square overflow-hidden border border-[#00ff00]">
                <img 
                    src={coverArtUrl} 
                    alt={data.release.title}
                    class="w-full h-full object-cover"
                />
            </div>

            <div class="flex flex-col gap-6">
                <h1 class="text-4xl font-bold tracking-wider uppercase text-[#ff00ff]">
                    {data.release.title}
                </h1>
                
                {#if data.release.artist}
                    <div>
                        <h2 class="text-sm text-[#00ffff] uppercase mb-1">Artist</h2>
                        <a 
                            href="/artists/{data.release.artist.slug}" 
                            class="text-lg text-[#00ff00] hover:text-[#ff00ff] transition-colors"
                        >
                            {data.release.artist.stage_name}
                        </a>
                    </div>
                {/if}

                {#if data.release.release_date}
                    <div>
                        <h2 class="text-sm text-[#00ffff] uppercase mb-1">Release Date</h2>
                        <p class="text-lg text-[#00ff00]">
                            {new Date(data.release.release_date).toLocaleDateString()}
                        </p>
                    </div>
                {/if}

                {#if data.release.description}
                    <div>
                        <h2 class="text-sm text-[#00ffff] uppercase mb-1">Description</h2>
                        <div class="text-lg text-[#00ff00]">{@html data.release.description}</div>
                    </div>
                {/if}

                {#if data.release.tracklist}
                    <div>
                        <h2 class="text-sm text-[#00ffff] uppercase mb-1">Tracklist</h2>
                        <div class="text-lg text-[#00ff00]">{@html data.release.tracklist}</div>
                    </div>
                {/if}

                <div class="flex gap-4 mt-4">
                    {#if data.release.bandcamp_url}
                        <Button 
                            variant="outline" 
                            class="border-[#00ff00] text-[#00ff00] hover:bg-[#00ff00] hover:text-black"
                        >
                            <a href={data.release.bandcamp_url} target="_blank" rel="noopener noreferrer">
                                Buy Digital
                            </a>
                        </Button>
                    {/if}
                    
                    {#if data.release.vinyl_url}
                        <Button 
                            variant="outline" 
                            class="border-[#00ff00] text-[#00ff00] hover:bg-[#00ff00] hover:text-black"
                        >
                            <a href={data.release.vinyl_url} target="_blank" rel="noopener noreferrer">
                                Buy Vinyl
                            </a>
                        </Button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</div> 