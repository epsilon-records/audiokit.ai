<script lang="ts">
  import type { PageData } from './$types';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { UserProfile } from 'svelte-clerk';

  let { data } = $props<{ data: PageData }>();
</script>

<SettingsContainer title="Account">
  <svelte:fragment slot="description">
    Manage your account settings and preferences.
  </svelte:fragment>

  <UserProfile />
</SettingsContainer>
