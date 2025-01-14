<script lang="ts">
  import type { PageData } from './$types';
  import ArtistImage from '$lib/components/ArtistImage.svelte';
  import ArtistInfoField from '$lib/components/ArtistInfoField.svelte';
  import ArtistSocialLinks from '$lib/components/ArtistSocialLinks.svelte';

  let { data } = $props<{ data: PageData }>();
</script>

<div class="min-h-screen bg-black text-[#00ff00]">
  <div class="container mx-auto px-4 pt-32 pb-12">
    <div class="flex justify-between items-center mb-8">
      <a
        href="/artists"
        class="inline-flex items-center gap-2 text-[#00ffff] hover:text-[#ff00ff] transition-colors"
      >
        <span class="text-2xl">←</span>
        <span class="uppercase tracking-wider">Back to Artists</span>
      </a>

      <a
        href={`/artists/${data.artist.id}/edit`}
        class="inline-flex items-center gap-2 px-4 py-2 bg-[#00ff00] text-black hover:bg-[#ff00ff] transition-colors rounded"
      >
        <span class="uppercase tracking-wider">Edit Artist</span>
      </a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
      <ArtistImage artist={data.artist} />

      <div class="flex flex-col gap-6">
        <h1 class="text-4xl font-bold tracking-wider uppercase text-[#ff00ff]">
          {data.artist.stage_name}
        </h1>

        <ArtistInfoField label="Real Name" value={data.artist.legal_name} />

        <ArtistInfoField label="Biography" value={data.artist.biography} />

        <ArtistInfoField label="Location" value={data.artist.country} />

        <ArtistSocialLinks
          links={[
            ...(data.artist.soundcloud
              ? [{ platform: 'soundcloud', url: data.artist.soundcloud }]
              : []),
            ...(data.artist.instagram
              ? [{ platform: 'instagram', url: data.artist.instagram }]
              : []),
            ...(data.artist.facebook ? [{ platform: 'facebook', url: data.artist.facebook }] : []),
            ...(data.artist.twitter ? [{ platform: 'twitter', url: data.artist.twitter }] : []),
            ...(data.artist.website ? [{ platform: 'website', url: data.artist.website }] : []),
          ]}
        />
      </div>
    </div>
  </div>
</div>
