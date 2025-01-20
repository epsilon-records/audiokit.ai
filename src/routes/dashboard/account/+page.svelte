<script lang="ts">
  import { UserProfile } from 'svelte-clerk';
  import { createClerkAppearance } from '$lib/config/clerk';
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Account Settings</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Manage your personal account settings and preferences.
    </p>
  </div>

  <div class="flex justify-center">
    <div class="rounded-lg p-2 mt-4 mb-8">
      <UserProfile appearance={createClerkAppearance()} />
    </div>
  </div>
</div>
