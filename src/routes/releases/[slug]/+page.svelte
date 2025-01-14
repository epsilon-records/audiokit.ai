<script lang="ts">
  import type { PageData } from './$types';
  import { pb } from '$lib/pocketbase';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import { Button } from '$lib/components/ui/button';

  let { data } = $props<{ data: PageData }>();

  const coverArtUrl = $derived(
    data.release.cover_artwork?.[0]
      ? pb.files.getURL(data.release, data.release.cover_artwork[0])
      : '/default-release.jpg',
  );
</script>

<PageContainer bgColor="bg-black" textColor="text-[#00ff00]">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
    <div class="aspect-square overflow-hidden border border-[#00ff00]">
      <img src={coverArtUrl} alt={data.release.title} class="w-full h-full object-cover" />
    </div>

    <div class="flex flex-col gap-6">
      <h1 class="text-4xl font-bold tracking-wider uppercase text-[#ff00ff]">
        {data.release.title}
      </h1>

      {#if data.release.expand?.tracks}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Artists</h2>
          <div class="flex flex-col gap-2">
            {#each [...new Set(data.release.expand.tracks
                  .flatMap((track) => track.expand?.primary_artists || [])
                  .map( (artist) => JSON.stringify( { name: artist.stage_name, slug: artist.slug }, ), ))].map( (artistStr) => JSON.parse(artistStr), ) as artist}
              <a
                href="/artists/{artist.slug}"
                class="text-lg text-[#00ff00] hover:text-[#ff00ff] transition-colors"
              >
                {artist.name}
              </a>
            {/each}
          </div>
        </div>
      {/if}

      {#if data.release.catalog_number}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Catalog Number</h2>
          <p class="text-lg text-[#00ff00]">{data.release.catalog_number}</p>
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
</PageContainer>
