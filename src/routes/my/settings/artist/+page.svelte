<script lang="ts">
  import type { PageData } from '../account copy/$types';
  import SettingsClerkContainer from '$lib/components/SettingsClerkContainer.svelte';
  import { OrganizationProfile } from 'svelte-clerk';

  let { data } = $props<{ data: PageData }>();
</script>

<SettingsClerkContainer>
  <OrganizationProfile />
</SettingsClerkContainer>
