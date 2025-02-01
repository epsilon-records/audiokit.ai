<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { artist } = $props<{
    artist: {
      artist_photos?: string[];
      stage_name: string;
    };
  }>();

  const imageUrl = '/default-artist.jpg';
</script>

<div class="relative">
  <ImageHandler
    src={imageUrl}
    alt={artist.stage_name}
    aspectRatio="aspect-[3/4]"
    class="rounded-lg border border-[#CFFF04]"
  />
</div>
