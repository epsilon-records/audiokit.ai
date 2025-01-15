<script lang="ts">
  import type { PageData } from './$types';
  import SettingsClerkContainer from '$lib/components/SettingsClerkContainer.svelte';
  import { UserProfile } from 'svelte-clerk';

  let { data } = $props<{ data: PageData }>();
</script>

<SettingsClerkContainer>
  <UserProfile />
</SettingsClerkContainer>
