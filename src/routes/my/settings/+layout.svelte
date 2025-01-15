<script lang="ts">
  import PageContainer from '$lib/components/PageContainer.svelte';
  import SettingsNav from '$lib/components/SettingsNav.svelte';
  import { OrganizationSwitcher } from 'svelte-clerk';

  let { children } = $props();
</script>

<PageContainer title="Settings" bgColor="bg-green-100" textColor="text-foreground">
  <div class="flex w-full h-full space-x-4">
    <OrganizationSwitcher />
    <SettingsNav />
    <div class="w-full">
      {@render children()}
    </div>
  </div>
</PageContainer>
