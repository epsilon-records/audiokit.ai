<script lang="ts">
  import { OrganizationProfile } from 'svelte-clerk';
  import { mode } from 'mode-watcher';
  import { neobrutalism, dark } from '@clerk/themes';
</script>

<div class="flex justify-center bg-background">
  <div class="bg-card rounded-lg p-2 mt-4 mb-8">
    <OrganizationProfile />
  </div>
</div>
