<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { goto } from '$app/navigation';
  import { PlusCircle } from 'lucide-svelte';

  let { data } = $props();
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Releases</h1>
    <p class="mt-2 text-lg text-muted-foreground">Manage your artist releases and distribution.</p>
  </div>

  {#if data.releases.length === 0}
    <Card>
      <CardHeader class="bg-gradient-to-r from-yellow-50 to-yellow-100 pb-4">
        <CardTitle>🎵 No releases found</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-muted-foreground">
          Get started by creating your first release to begin distribution.
        </p>
        <div class="mt-4 space-y-2">
          <a
            href="/dashboard/releases/create"
            class="btn btn-primary gap-2"
            class:btn-disabled={!data.hasActiveSubscription}
          >
            <PlusCircle class="h-4 w-4" />
            Create Release
          </a>

          {#if !data.hasActiveSubscription}
            <div class="flex items-center gap-2">
              <Badge variant="destructive">
                You need an active subscription to create releases.
                <a
                  href="/join"
                  class="ml-2 inline-flex items-center rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition-colors"
                >
                  Enable Services
                </a>
              </Badge>
            </div>
          {/if}
        </div>
      </CardContent>
    </Card>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each data.releases as release}
        <Card class="hover:shadow-md transition-shadow">
          <div class="aspect-square">
            <img
              src={'/default-release.jpg'}
              alt={release.release_title}
              class="object-cover w-full h-full rounded-t-lg"
            />
          </div>
          <CardContent class="p-4 space-y-2">
            <h3 class="font-semibold truncate">{release.release_title}</h3>
            <p class="text-sm text-muted-foreground">{release.release_date}</p>
            <div class="flex justify-between items-center mt-4">
              <Badge variant={release.status === 'published' ? 'success' : 'warning'}>
                {release.status}
              </Badge>
              <button
                class="btn btn-ghost btn-sm"
                onclick={() => goto(`/dashboard/releases/${release.id}`)}
              >
                Edit
              </button>
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {/if}
</div>
