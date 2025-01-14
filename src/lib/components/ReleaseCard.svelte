<script lang="ts">
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
</script>

<a href="/releases/{release.slug}" class="block group">
  <div class="aspect-square overflow-hidden border border-[#00ff00]">
    <img
      src={release.cover_artwork?.[0]
        ? pb.files.getURL(release, release.cover_artwork[0])
        : '/default-release.jpg'}
      alt={release.title}
      class="w-full h-full object-cover transition-transform group-hover:scale-105"
    />
  </div>
  <h2 class="mt-4 text-xl text-[#00ff00] group-hover:text-[#ff00ff] transition-colors">
    {release.title}
  </h2>
  <p class="text-[#00ffff]">{release.expand?.artist?.stage_name}</p>
</a>
