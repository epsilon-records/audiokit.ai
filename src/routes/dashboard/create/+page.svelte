<script lang="ts">
  import { Button } from '$lib/components/ui/button';
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Create New</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Start creating new artists or releases for your catalog.
    </p>
  </div>

  <div class="max-w-2xl mx-auto text-center">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="flex flex-col h-full bg-card rounded-lg p-6 shadow-lg">
        <div class="flex-1">
          <h2 class="text-2xl font-bold mb-4">Create New Artist</h2>
          <p class="text-muted-foreground mb-4">
            Create and manage your artist organization with team collaboration tools.
          </p>
        </div>
        <div class="mt-auto">
          <Button href="/dashboard/create-artist" class="w-full h-12" size="lg">
            Create New Artist
          </Button>
        </div>
      </div>
      <div class="flex flex-col h-full bg-card rounded-lg p-6 shadow-lg">
        <div class="flex-1">
          <h2 class="text-2xl font-bold mb-4">Create New Release</h2>
          <p class="text-muted-foreground mb-4">
            Create and distribute your next release across all major platforms with just a few
            clicks.
          </p>
        </div>
        <div class="mt-auto">
          <Button href="/dashboard/releases/new" class="w-full h-12" size="lg">
            Create New Release
          </Button>
        </div>
      </div>
    </div>
  </div>
</div>
