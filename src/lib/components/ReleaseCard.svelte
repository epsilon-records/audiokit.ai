<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { release, pb } = $props<{
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
    pb: any;
  }>();

  const imageUrl = $derived(
    release.cover_artwork?.[0]
      ? pb.files.getURL(release, release.cover_artwork[0])
      : '/default-release.jpg',
  );

  const artistNames = $derived(
    [
      ...new Set(
        release.expand.tracks.flatMap((track: any) =>
          track.expand.primary_artists.map((artist: any) => artist.stage_name),
        ),
      ),
    ].join(' • '),
  );
</script>

<a href="/releases/{release.slug}" class="block group">
  <ImageHandler src={imageUrl} alt={release.title} class="border border-[#00ff00]" />
  <h2 class="mt-4 text-xl text-[#00ff00] group-hover:text-[#ff00ff] transition-colors">
    {release.title}
  </h2>
  {#if artistNames}
    <p class="text-yellow-500 group-hover:text-[#ff00ff] transition-colors">
      {artistNames}
    </p>
  {/if}
</a>
