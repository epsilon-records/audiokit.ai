<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Button } from '$lib/components/ui/button';

  let { data } = $props();

  let albums = $derived(data.albums);

  $inspect(albums); // Check the value of albums in the console
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Albums</h1>
    <p class="mt-2 text-lg text-muted-foreground">View all your artist albums and distribution.</p>
  </div>

  {#if albums.length === 0}
    <Card>
      <CardHeader class="bg-gradient-to-r from-yellow-50 to-yellow-100 pb-4">
        <CardTitle>🎵 No albums found</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-muted-foreground">
          Connect your music distribution accounts to import your albums and start managing your
          releases.
        </p>
        <div class="mt-4">
          <Button href="/dashboard/profile">Connect Accounts</Button>
        </div>
      </CardContent>
    </Card>
  {:else}
    <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
      {#each albums as album}
        <Card>
          <a href="/dashboard/albums/{album.id}" class="block">
            <img
              src={album.artwork}
              alt={album.title}
              class="h-48 w-full object-cover rounded-t-lg"
            />
          </a>
          <CardContent>
            <a href="/dashboard/albums/{album.id}" class="block">
              <h3 class="text-xl font-semibold">{album.title}</h3>
            </a>
            <p class="mt-1 text-sm text-muted-foreground">
              {album.releaseDate}
            </p>
            <div class="mt-4 flex flex-wrap gap-2">
              {#each album.genres as genre}
                <Badge>{genre}</Badge>
              {/each}
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {/if}
</div>
