<script lang="ts">
  import PageContainer from '$lib/components/PageContainer.svelte';
  import SettingsNav from '$lib/components/SettingsNav.svelte';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';

  let { children } = $props();
</script>

<PageContainer title="Settings" bgColor="bg-green-100" textColor="text-foreground">
  <div class="flex w-full h-full space-x-4">
    <div class="pt-2">
      <OrganizationSwitcher
        appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
        hidePersonal={true}
        afterCreateOrganizationUrl="/profile"
        afterSelectOrganizationUrl="/profile"
      />
    </div>
    <SettingsNav />
    <div class="w-full">
      {@render children()}
    </div>
  </div>
</PageContainer>
