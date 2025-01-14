<script lang="ts">
  import { pb } from '$lib/pocketbase';
  import PageContainer from '$lib/components/PageContainer.svelte';
  import GridContainer from '$lib/components/GridContainer.svelte';
  import ReleaseCard from '$lib/components/ReleaseCard.svelte';

  let { data } = $props<{ data: { releases: any[] } }>();
</script>

<PageContainer title="Releases" bgColor="bg-teal-100" textColor="text-[#00ff00]">
  <GridContainer cols="grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
    {#each data.releases as release}
      <ReleaseCard {release} {pb} />
    {/each}
  </GridContainer>
</PageContainer>
