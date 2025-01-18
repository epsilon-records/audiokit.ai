<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { pb } from '$lib/pocketbase';
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
      <CardHeader>
        <CardTitle>No releases found</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-muted-foreground">
          Get started by creating your first release to begin distribution.
        </p>
        <div class="mt-4">
          <Button href="/dashboard/releases/create" variant="default">
            <PlusCircle class="mr-2 h-4 w-4" />
            Create Release
          </Button>
        </div>
      </CardContent>
    </Card>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each data.releases as release}
        <Card class="hover:shadow-md transition-shadow">
          <div class="aspect-square">
            <img
              src={release.cover_artwork?.[0]
                ? pb.files.getURL(release, release.cover_artwork[0])
                : '/default-release.jpg'}
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
              <Button
                variant="ghost"
                size="sm"
                on:click={() => goto(`/dashboard/releases/${release.id}`)}
              >
                Edit
              </Button>
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {/if}
</div>
