<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { OrganizationProfile } from 'svelte-clerk';
  import { OrganizationSwitcher } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<SettingsContainer title="Team Settings">
  <svelte:fragment slot="description">Manage your team settings.</svelte:fragment>
  <OrganizationProfile />
</SettingsContainer>
