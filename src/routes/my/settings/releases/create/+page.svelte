<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { cn } from '$lib/utils';
  import { pb } from '$lib/pocketbase';

  let { data } = $props();
</script>

<SettingsContainer title="Manage Releases">
  <svelte:fragment slot="description">Manage your artist releases.</svelte:fragment>
  <div class="space-y-4 bg-yellow-100 rounded-lg border-2 border-yellow-200 p-6">
    <h2 class="text-2xl font-bold">Create a New Release</h2>
    <p class="text-lg text-gray-700">
      Fill out the form below to create a new release for your artist.
    </p>
  </div>
</SettingsContainer>
