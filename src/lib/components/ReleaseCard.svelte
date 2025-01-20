<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { release } = $props<{
    release: {
      slug: string;
      cover_artwork?: string[];
      title: string;
      expand: {
        tracks: {
          primary_artists: {
            stage_name: string;
          }[];
        }[];
      };
    };
  }>();

  const imageUrl = '/default-release.jpg';

  const artistNames = $derived(
    [
      ...new Set(
        release.expand.tracks.flatMap((track: any) =>
          track.expand.primary_artists.map((artist: any) => artist.stage_name)
        )
      ),
    ].join(' • ')
  );
</script>

<a href="/releases/{release.slug}" class="block group">
  <ImageHandler src={imageUrl} alt={release.title} />
  <h2 class="mt-4 text-xl text-slate-800 group-hover:text-[#ff00ff] transition-colors text-center">
    {release.release_title}
  </h2>
  {#if artistNames}
    <p class="text-slate-500 group-hover:text-[#ff00ff] transition-colors text-center">
      {artistNames}
    </p>
  {/if}
</a>
