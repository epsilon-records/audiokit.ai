<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Button } from '$lib/components/ui/button';

  let { data } = $props<{ tracks: Track[] }>();
  let tracks = $derived(data.tracks);
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Tracks</h1>
    <p class="mt-2 text-lg text-muted-foreground">View and manage your tracks.</p>
  </div>

  {#if tracks.length === 0}
    <Card>
      <CardHeader class="bg-gradient-to-r from-yellow-50 to-yellow-100 pb-4">
        <CardTitle>🎵 No tracks found</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-muted-foreground">
          Connect your music distribution accounts to import your tracks and start managing your
          releases.
        </p>
        <div class="mt-4">
          <Button href="/dashboard/profile">Connect Accounts</Button>
        </div>
      </CardContent>
    </Card>
  {:else}
    <div class="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
      {#each tracks as track}
        <Card>
          <a href="/dashboard/tracks/{track.uuid}" class="block">
            <img
              src={track.imageUrl}
              alt={track.name}
              class="h-48 w-full object-cover rounded-t-lg"
            />
          </a>
          <CardContent>
            <a href="/dashboard/tracks/{track.uuid}" class="block">
              <h3 class="text-xl font-semibold">{track.name}</h3>
            </a>
            <p class="mt-1 text-sm text-muted-foreground">
              {new Date(track.releaseDate).toLocaleDateString()}
            </p>
            <div class="mt-2">
              <p class="text-sm text-muted-foreground">
                {track.artists.map((artist) => artist.name).join(', ')}
              </p>
            </div>
            <div class="mt-4 flex flex-wrap gap-2">
              {#each track.genres as genre}
                <Badge>{genre.root}</Badge>
              {/each}
            </div>
          </CardContent>
        </Card>
      {/each}
    </div>
  {/if}
</div>
