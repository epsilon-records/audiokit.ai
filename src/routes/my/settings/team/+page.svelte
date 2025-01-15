<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { OrganizationProfile } from 'svelte-clerk';
</script>

<SettingsContainer title="Team Settings">
  <svelte:fragment slot="description">Manage your team settings.</svelte:fragment>
  <OrganizationProfile />
</SettingsContainer>
