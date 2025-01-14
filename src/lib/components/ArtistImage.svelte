<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';
  import { pb } from '$lib/pocketbase';

  let { artist } = $props<{
    artist: {
      artist_photos?: string[];
      stage_name: string;
    };
  }>();

  const imageUrl = $derived(
    artist.artist_photos?.[0]
      ? pb.files.getURL(artist, artist.artist_photos[0])
      : '/default-artist.jpg',
  );
</script>

<div class="relative">
  <ImageHandler
    src={imageUrl}
    alt={artist.stage_name}
    aspectRatio="aspect-[3/4]"
    class="rounded-lg border border-[#CFFF04]"
  />
  {#if artist.artist_photos && artist.artist_photos.length > 1}
    <div class="absolute bottom-4 right-4 bg-black/50 px-3 py-1 rounded-full text-sm text-white">
      +{artist.artist_photos.length - 1} more
    </div>
  {/if}
</div>
