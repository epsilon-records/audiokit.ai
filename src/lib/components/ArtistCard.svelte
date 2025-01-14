<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { artist, pb } = $props<{
    artist: {
      slug: string;
      artist_photos?: string[];
      stage_name: string;
    };
    pb: any;
  }>();

  const imageUrl = $derived(
    artist.artist_photos?.[0]
      ? pb.files.getURL(artist, artist.artist_photos[0])
      : '/default-artist.jpg',
  );
</script>

<a href="/artists/{artist.slug}" class="block group">
  <ImageHandler src={imageUrl} alt={artist.stage_name} class="border border-[#CFFF04]" />
  <h2 class="mt-4 text-xl text-yellow-500 group-hover:text-[#ff00ff] transition-colors">
    {artist.stage_name}
  </h2>
</a>
