<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { UserProfile } from 'svelte-clerk';
</script>

<SettingsContainer title="Account Settings">
  <svelte:fragment slot="description">Manage your account settings.</svelte:fragment>
  <UserProfile />
</SettingsContainer>
