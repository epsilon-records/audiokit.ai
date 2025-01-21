<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { PlusCircle } from 'lucide-svelte';

  let { data } = $props();
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Releases</h1>
    <p class="mt-2 text-lg text-muted-foreground">Manage your artist releases and distribution.</p>
  </div>

  {#if true}
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
            class:btn-disabled={!data.auth.hasActiveSubscription}
          >
            <PlusCircle class="h-4 w-4" />
            Create Release
          </a>

          {#if !data.auth.hasActiveSubscription}
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
  {/if}
</div>
