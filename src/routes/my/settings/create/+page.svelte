<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { CreateOrganization } from 'svelte-clerk';
</script>

<SettingsContainer title="New Artist">
  <svelte:fragment slot="description">Manage your team settings.</svelte:fragment>
  <CreateOrganization />
</SettingsContainer>
