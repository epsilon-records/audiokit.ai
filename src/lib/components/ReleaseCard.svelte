<script lang="ts">
  import ImageHandler from './ImageHandler.svelte';

  let { release, pb } = $props<{
    release: {
      slug: string;
      cover_artwork?: string[];
      title: string;
      expand?: {
        artist?: {
          stage_name: string;
        };
      };
    };
    pb: any;
  }>();

  const imageUrl = $derived(
    release.cover_artwork?.[0]
      ? pb.files.getURL(release, release.cover_artwork[0])
      : '/default-release.jpg',
  );
</script>

<a href="/releases/{release.slug}" class="block group">
  <ImageHandler src={imageUrl} alt={release.title} class="border border-[#00ff00]" />
  <h2 class="mt-4 text-xl text-[#00ff00] group-hover:text-[#ff00ff] transition-colors">
    {release.title}
  </h2>
  {#if release.expand?.artist}
    <p class="text-[#00ffff]">{release.expand.artist.stage_name}</p>
  {/if}
</a>
