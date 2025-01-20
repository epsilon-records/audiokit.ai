<script lang="ts">
  import { CreateOrganization } from 'svelte-clerk';
  import { createClerkAppearance } from '$lib/config/clerk';
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Manage New Artist</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Create an organization to manage your artist profile, team members, and releases.
    </p>
  </div>

  <div class="flex justify-center">
    <div class="rounded-lg p-2 mt-4 mb-8">
      <CreateOrganization appearance={createClerkAppearance()} />
    </div>
  </div>
</div>
