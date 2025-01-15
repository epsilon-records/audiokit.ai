<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { CreateOrganization } from 'svelte-clerk';
</script>

<SettingsContainer title="New Artist">
  <svelte:fragment slot="description">Create a new artist profile.</svelte:fragment>
  <CreateOrganization />
</SettingsContainer>
