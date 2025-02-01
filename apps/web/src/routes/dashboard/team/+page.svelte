<script lang="ts">
  import { OrganizationProfile } from 'svelte-clerk';
  import { createClerkAppearance } from '$lib/config/clerk';
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Team Management</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Manage your team members, roles, and permissions.
    </p>
  </div>

  <div class="flex justify-center">
    <div class="rounded-lg p-2 mt-4 mb-8">
      <OrganizationProfile appearance={createClerkAppearance()} />
    </div>
  </div>
</div>
