<script lang="ts">
  import PageContainer from '$lib/components/PageContainer.svelte';
  import DashboardNav from '$lib/components/DashboardNav.svelte';
  import type { Snippet } from 'svelte';

  let { children } = $props<{ children: Snippet }>();
</script>

<PageContainer title="Settings" bgColor="bg-green-100" textColor="text-foreground">
  <div class="flex flex-col lg:flex-row gap-6 lg:gap-8">
    <aside class="w-full lg:w-64 flex-shrink-0">
      <DashboardNav />
    </aside>
    <div class="flex-1 min-w-0">
      {@render children()}
    </div>
  </div>
</PageContainer>
