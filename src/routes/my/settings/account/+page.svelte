<script lang="ts">
  import SettingsClerkContainer from '$lib/components/SettingsClerkContainer.svelte';
  import { UserProfile } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<SettingsClerkContainer>
  <div class="space-y-4">
    <h3 class="text-2xl font-semibold">Select Artist</h3>
    <div class="bg-blue-100 rounded-lg">
      <OrganizationSwitcher
        appearance={{ baseTheme: $mode === 'dark' ? dark : neobrutalism }}
        hidePersonal={true}
        afterCreateOrganizationUrl="/my/settings/profile"
        afterSelectOrganizationUrl="/my/settings/profile"
      />
    </div>
    <p class="text-muted-foreground">
      Choose the artist profile you want to edit. You can switch between different artists or create
      a new artist profile.
    </p>
  </div>
  <UserProfile />
</SettingsClerkContainer>
