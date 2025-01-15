<script lang="ts">
  import type { PageData } from './$types';
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { UserProfile } from 'svelte-clerk';

  let { data } = $props<{ data: PageData }>();
</script>

<SettingsContainer title="Account">
  <UserProfile />
</SettingsContainer>
