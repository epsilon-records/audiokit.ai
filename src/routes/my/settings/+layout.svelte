<script lang="ts">
  import PageContainer from '$lib/components/PageContainer.svelte';
  import DashboardNav from '$lib/components/DashboardNav.svelte';
  import type { Snippet } from 'svelte';

  let { children } = $props<{ children: Snippet }>();
</script>

<PageContainer title="Dashboard" bgColor="bg-green-100" textColor="text-foreground">
  <div class="flex w-full h-full space-x-4">
    <DashboardNav />
    <div class="w-full">
      {@render children()}
    </div>
  </div>
</PageContainer>
