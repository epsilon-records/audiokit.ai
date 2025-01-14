<script lang="ts">
  import PageContainer from '$lib/components/PageContainer.svelte';
  import SettingsNav from '$lib/components/SettingsNav.svelte';

  let { children } = $props();
</script>

<PageContainer title="Settings" bgColor="bg-background" textColor="text-foreground">
  <div class="flex w-full h-full space-x-4">
    <SettingsNav />
    <div class="w-full">
      {@render children()}
    </div>
  </div>
</PageContainer>
