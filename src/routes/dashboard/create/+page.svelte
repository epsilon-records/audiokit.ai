<script lang="ts">
  import { Button } from '$lib/components/ui/button';
</script>

<div class="container mx-auto px-4 py-16">
  <div class="max-w-2xl mx-auto text-center">
    <h1 class="text-4xl font-bold mb-8">What would you like to create?</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="flex flex-col h-full bg-card rounded-lg p-6 shadow-lg">
        <div class="flex-1">
          <h2 class="text-2xl font-bold mb-4">Create Artist Profile</h2>
          <p class="text-muted-foreground mb-4">
            Create and manage your artist organization with team collaboration tools.
          </p>
        </div>
        <div class="mt-auto">
          <a
            href="/dashboard/create-artist"
            class="inline-flex w-full h-12 items-center justify-center btn btn-primary text-pink-100"
          >
            Create Artist Profile
          </a>
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
          <a
            href="/dashboard/releases/new"
            class="inline-flex w-full h-12 items-center justify-center btn btn-primary text-pink-100"
          >
            Create New Release
          </a>
        </div>
      </div>
    </div>
  </div>
</div>
