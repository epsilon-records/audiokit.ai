<script lang="ts">
    const releases = [
        {
            id: 1,
            title: "Neon Dreams",
            artist: "KLØT",
            thumbnail: "https://picsum.photos/seed/release1/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 2,
            title: "Digital Wasteland",
            artist: "Neurøsis",
            thumbnail: "https://picsum.photos/seed/release2/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 3,
            title: "Synthetic Reality",
            artist: "VØID",
            thumbnail: "https://picsum.photos/seed/release3/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 4,
            title: "Binary Sunset",
            artist: "Synthex",
            thumbnail: "https://picsum.photos/seed/release4/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 5,
            title: "Midnight Protocol",
            artist: "DRKRM",
            thumbnail: "https://picsum.photos/seed/release5/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 6,
            title: "System Failure",
            artist: "Pulse//Error",
            thumbnail: "https://picsum.photos/seed/release6/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 7,
            title: "Neural Network",
            artist: "Binary Ghost",
            thumbnail: "https://picsum.photos/seed/release7/800/800",
            class: "opacity-90 hover:opacity-100"
        },
        {
            id: 8,
            title: "Quantum State",
            artist: "Æther",
            thumbnail: "https://picsum.photos/seed/release8/800/800",
            class: "opacity-90 hover:opacity-100"
        }
    ];
</script>

<div class="min-h-screen bg-black text-white">
    <div class="container mx-auto px-4 pt-32 pb-12">
        <h1 class="text-4xl font-bold mb-8 tracking-wider uppercase relative inline-block after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-1/2 after:h-[2px] after:bg-white after:animate-pulse">
            Our Releases
        </h1>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {#each releases as release (release.id)}
                <div class="relative group {release.class} overflow-hidden rounded-none border border-zinc-800 hover:border-zinc-600 transition-colors duration-500">
                    <img 
                        src={release.thumbnail} 
                        alt={release.title}
                        class="w-full h-full object-cover aspect-square transition-all duration-500 group-hover:scale-105 group-hover:opacity-80"
                    />
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500 flex flex-col justify-end p-6">
                        <span class="text-white text-xl font-light tracking-wider uppercase transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                            {release.title}
                        </span>
                        <span class="text-zinc-400 text-sm tracking-wider transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500 delay-75">
                            {release.artist}
                        </span>
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div> 