<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<SettingsContainer title="Security">
  <svelte:fragment slot="description">
    Manage your security settings and preferences.
  </svelte:fragment>

  <!-- Security settings form -->
</SettingsContainer>
