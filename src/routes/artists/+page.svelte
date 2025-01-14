<script lang="ts">
  import { pb } from '$lib/pocketbase';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import GridContainer from '$lib/components/GridContainer.svelte';
  import ArtistCard from '$lib/components/ArtistCard.svelte';

  let { data } = $props<{ data: { artists: any[] } }>();
</script>

<PageContainer title="Artists" bgColor="bg-pink-100" textColor="text-pink-500">
  <GridContainer cols="grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
    {#each data.artists as artist}
      {#if artist.slug}
        <ArtistCard {artist} {pb} />
      {/if}
    {/each}
  </GridContainer>
</PageContainer>
