<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import SuperDebug from 'sveltekit-superforms';

  let { data } = $props();
</script>

<SettingsContainer title="Manage Releases">
  <!-- {#if $message}
    <h3>{$message}</h3>
  {/if} -->
  <svelte:fragment slot="description">Manage your artist releases.</svelte:fragment>
  <div class="space-y-4 bg-white rounded-lg border border-gray-200 p-6">
    <!-- Debug Data -->
    <!-- <SuperDebug data={$formData} /> -->
  </div>
</SettingsContainer>
