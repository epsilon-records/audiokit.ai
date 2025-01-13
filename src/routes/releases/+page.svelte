<script lang="ts">
    import { pb } from '$lib/pocketbase';
    let { data } = $props<{ data: { releases: any[] } }>();
</script>

<div class="min-h-screen bg-black">
    <div class="container mx-auto px-4 pt-32 pb-12">
        <h1 class="text-4xl font-bold text-[#00ff00] mb-12">Releases</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {#each data.releases as release}
                <a 
                    href="/releases/{release.slug}" 
                    class="block group"
                >
                    <div class="aspect-square overflow-hidden border border-[#00ff00]">
                        <img 
                            src={release.cover_artwork?.[0] ? pb.files.getURL(release, release.cover_artwork[0]) : '/default-release.jpg'} 
                            alt={release.title}
                            class="w-full h-full object-cover transition-transform group-hover:scale-105"
                        />
                    </div>
                    <h2 class="mt-4 text-xl text-[#00ff00] group-hover:text-[#ff00ff] transition-colors">
                        {release.title}
                    </h2>
                    <p class="text-[#00ffff]">{release.expand?.artist?.stage_name}</p>
                </a>
            {/each}
        </div>
    </div>
</div> 