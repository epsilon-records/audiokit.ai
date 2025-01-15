<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { OrganizationProfile } from 'svelte-clerk';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<SettingsContainer title="Select Artist">
  <svelte:fragment slot="description">Select the artist profile you want to edit.</svelte:fragment>
  <div class="space-y-4 bg-pink-100 rounded-lg border-2 border-pink-200 p-6">
    <h3 class="text-2xl font-semibold">Choose Profile</h3>
    <div class="rounded-lg">
      <OrganizationSwitcher
        appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
        hidePersonal={true}
        afterCreateOrganizationUrl="/my/settings/profile"
        afterSelectOrganizationUrl="/my/settings/profile"
      />
    </div>
    <p class="text-muted-foreground">
      Choose the artist profile you want to edit. You can switch between different artists or <a
        href="/my/settings/create"
        class="text-cyan-400 font-bold hover:text-cyan-600 transition-colors hover:underline"
        >create a new artist profile</a
      >, also known as an organization.
    </p>
  </div>
</SettingsContainer>
