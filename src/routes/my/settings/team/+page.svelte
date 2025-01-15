<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { OrganizationProfile } from 'svelte-clerk';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<SettingsContainer title="Team Settings">
  <svelte:fragment slot="description">Manage your team settings.</svelte:fragment>
  <div class="space-y-4 bg-white rounded-lg border border-gray-200 p-6">
    <h3 class="text-2xl font-semibold">Select Artist</h3>
    <div class="rounded-lg">
      <OrganizationSwitcher
        appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
        hidePersonal={true}
        afterCreateOrganizationUrl="/my/settings/team"
        afterSelectOrganizationUrl="/my/settings/team"
      />
    </div>
    <p class="text-muted-foreground">
      Choose the artist profile you want to edit. You can switch between different artists or create
      a new artist profile.
    </p>
  </div>
  <OrganizationProfile />
</SettingsContainer>
