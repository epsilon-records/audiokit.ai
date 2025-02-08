<script lang="ts">
  import { CreateOrganization } from 'svelte-clerk';
  import { createClerkAppearance } from '$lib/config/clerk';
  import { Alert, AlertDescription, AlertTitle } from '$lib/components/ui/alert';
  import { LucideAlertTriangle } from 'lucide-svelte';
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Manage New Artist</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Create an organization to manage your artist profile, team members, and releases.
    </p>
  </div>

  <Alert class="mb-8" variant="destructive">
    <LucideAlertTriangle class="h-4 w-4" />
    <AlertTitle>Important: Choose Your Artist Name Carefully</AlertTitle>
    <AlertDescription class="text-muted-foreground">
      The organization name you enter here will be used as your public artist or stage name. It will
      be displayed on your profile, releases, and cannot be changed later. Please make sure to enter
      the exact spelling and capitalization you want to use for your artist identity. If you have
      previously released music under this name on any digital service provider (DSP), ensure the
      name matches exactly to avoid any conflicts or issues.
    </AlertDescription>
  </Alert>

  <div class="flex justify-center">
    <div class="rounded-lg p-2 mt-4 mb-8">
      <CreateOrganization appearance={createClerkAppearance()} />
    </div>
  </div>
</div>
