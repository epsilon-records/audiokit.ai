<script lang="ts">
  import { pb } from '$lib/pocketbase';
  let { data } = $props();
</script>

<div class="min-h-screen bg-pink-100">
  <div class="container mx-auto px-4 pt-32 pb-12">
    <h1 class="text-4xl font-bold text-green-400 mb-12">Artists</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {#each data.artists as artist}
        {#if artist.slug}
          <a href="/artists/{artist.slug}" class="block group">
            <div class="aspect-square overflow-hidden border border-[#CFFF04]">
              <img
                src={artist.artist_photos?.[0]
                  ? pb.files.getURL(artist, artist.artist_photos[0])
                  : '/default-artist.jpg'}
                alt={artist.stage_name}
                class="w-full h-full object-cover transition-transform group-hover:scale-105"
              />
            </div>
            <h2 class="mt-4 text-xl text-yellow-500 group-hover:text-[#ff00ff] transition-colors">
              {artist.stage_name}
            </h2>
          </a>
        {/if}
      {/each}
    </div>
  </div>
</div>
