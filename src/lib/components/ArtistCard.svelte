<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { artist } = $props<{
    artist: {
      slug: string;
      artist_photos?: string[];
      stage_name: string;
    };
  }>();

  const imageUrl = '/default-artist.jpg';
</script>

<a href="/artists/{artist.slug}" class="block group">
  <ImageHandler src={imageUrl} alt={artist.stage_name} class="border-2 border-[#CFFF04]" />
  <h2 class="mt-4 text-xl text-slate-500 group-hover:text-[#ff00ff] transition-colors">
    {artist.stage_name}
  </h2>
</a>
