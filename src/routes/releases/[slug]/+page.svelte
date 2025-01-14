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
        {data.release.release_title}
        {#if data.release.release_version}
          <span class="text-[#00ffff]">({data.release.release_version})</span>
        {/if}
      </h1>

      {#if data.release.expand?.genre}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Genre</h2>
          <p class="text-lg text-[#00ff00]">
            {data.release.expand.genre.name}
            {#if data.release.expand?.subgenre}
              / {data.release.expand.subgenre.name}
            {/if}
          </p>
        </div>
      {/if}

      {#if data.release.expand?.label}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Label</h2>
          <p class="text-lg text-[#00ff00]">{data.release.expand.label.name}</p>
        </div>
      {/if}

      {#if data.release.upc_code}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">UPC</h2>
          <p class="text-lg text-[#00ff00]">{data.release.upc_code}</p>
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

      {#if data.release.is_compilation}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Release Type</h2>
          <p class="text-lg text-[#00ff00]">Compilation</p>
        </div>
      {/if}

      {#if data.release.expand?.language}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Language</h2>
          <p class="text-lg text-[#00ff00]">{data.release.expand.language.name}</p>
        </div>
      {/if}

      {#if data.release.description}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Description</h2>
          <div class="text-lg text-[#00ff00]">{@html data.release.description}</div>
        </div>
      {/if}

      {#if data.release.expand?.tracks}
        <div>
          <h2 class="text-sm text-[#00ffff] uppercase mb-1">Tracklist</h2>
          <div class="flex flex-col gap-2 text-lg text-[#00ff00]">
            {#each data.release.expand.tracks as track, i}
              <div>
                {i + 1}. {track.track_title}
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <div class="flex gap-4 mt-4">
        {#if data.release.bandcamp}
          <Button
            variant="outline"
            class="border-[#00ffff] text-black hover:bg-[#00ffff] hover:text-black transition-colors"
          >
            <a href={data.release.bandcamp} target="_blank" rel="noopener noreferrer">Buy Digital</a
            >
          </Button>
        {/if}

        {#if data.release.vinyl}
          <Button
            variant="outline"
            class="border-[#ff00ff] text-black hover:bg-[#ff00ff] hover:text-black transition-colors"
          >
            <a href={data.release.vinyl} target="_blank" rel="noopener noreferrer">Buy Vinyl</a>
          </Button>
        {/if}
      </div>
    </div>
  </div>
</PageContainer>
