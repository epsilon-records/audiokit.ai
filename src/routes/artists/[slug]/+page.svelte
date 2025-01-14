<script lang="ts">
  import type { PageData } from './$types';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import ArtistImage from '$lib/components/ArtistImage.svelte';
  import ArtistInfoField from '$lib/components/ArtistInfoField.svelte';
  import ArtistSocialLinks from '$lib/components/ArtistSocialLinks.svelte';
  import BackButton from '$lib/components/BackButton.svelte';

  let { data } = $props<{ data: PageData }>();
</script>

<PageContainer bgColor="bg-black" textColor="text-[#00ff00]">
  <div class="flex justify-between items-center mb-8">
    <BackButton href="/artists" text="Back to Artists" />
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
      <ArtistSocialLinks links={data.artist.socialLinks} />
    </div>
  </div>
</PageContainer>
