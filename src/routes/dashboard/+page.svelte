<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { fly } from 'svelte/transition';
  import { AlertCircle } from 'lucide-svelte';
  import { Badge } from '$lib/components/ui/badge';
  import { formatNumber } from '$lib/utils/format';

  interface PageData {
    stats?: {
      metadata: typeof defaultMetadata;
      streaming?: typeof defaultStreaming;
      followers?: typeof defaultFollowers;
    };
    hasActiveSubscription: boolean;
    user: {
      id: string;
      imageUrl: string;
    };
  }

  let { data } = $props<{ data: PageData }>();
  let { stats, hasActiveSubscription, user, org } = data;

  let artistPhoto = $state(org.imageUrl);

  let defaultMetadata = {
    type: 'artist',
    object: {
      uuid: 'real-uuid-1234',
      slug: 'real-artist',
      name: 'Real Artist',
      appUrl: 'https://example.com/real-artist',
      imageUrl: 'https://example.com/real-artist.jpg',
      countryCode: 'US',
      genres: [
        {
          root: 'Real Genre',
          sub: ['Subgenre A', 'Subgenre B'],
        },
      ],
      biography: 'This is a real artist biography.',
      isni: '1234567890123456',
      ipi: '12345678901',
      gender: 'male',
      type: 'entity',
      birthDate: '1980-01-01T00:00:00+00:00',
    },
    errors: [],
  };

  let defaultStreaming = {
    platform: 'Spotify',
    streams: 1000000,
    listeners: 250000,
    playlists: 1500,
    engagement: 750000,
    errors: [],
  };

  let defaultFollowers = {
    platform: 'Instagram',
    followers: 50000,
    engagement: 25000,
    views: 1000000,
    errors: [],
  };
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Overview</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Get insights into your performance metrics and manage your artist profile.
    </p>
    {#if !stats}
      <div class="mt-4" in:fly={{ y: 20, duration: 400, delay: 200 }}>
        <Badge
          variant="outline"
          class="bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800"
        >
          <AlertCircle class="h-4 w-4 mr-2" />
          No statistics are available yet. Connect your platforms to start tracking your performance.
        </Badge>
      </div>
    {/if}
  </div>

  <div class="space-y-8">
    <!-- Artist Information -->
    <div in:fly={{ y: 20, duration: 400, delay: 300 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-green-500 to-emerald-500"
        >
          Artist Information
        </h2>
      </div>
      {#if stats?.metadata}
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 pb-6"
            >
              <CardTitle>👤 Artist Details</CardTitle>
            </CardHeader>
            <CardContent class="pt-6 space-y-4 flex justify-between">
              <div class="flex-1 space-y-4">
                <div>
                  <p class="text-sm text-muted-foreground">Name</p>
                  <p class="text-lg font-semibold">{stats.metadata.object.name}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Type</p>
                  <p class="text-lg font-semibold capitalize">{stats.metadata.object.type}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Country</p>
                  <p class="text-lg font-semibold">{stats.metadata.object.countryCode}</p>
                </div>
              </div>
              <div class="flex justify-center items-center pr-8">
                <div class="w-48 h-48 m-4 flex-shrink-0">
                  <img
                    src={artistPhoto}
                    alt="Artist"
                    class="w-full h-full rounded-full object-cover"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900 pb-6"
            >
              <CardTitle>🎵 Genres</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              {#each stats.metadata.object.genres as genre}
                <div class="mb-4">
                  <p class="text-lg font-semibold capitalize">{genre.root}</p>
                  {#if genre.sub.length > 0}
                    <div class="flex flex-wrap gap-2 mt-2">
                      {#each genre.sub as subGenre}
                        <Badge variant="secondary" class="capitalize">{subGenre}</Badge>
                      {/each}
                    </div>
                  {/if}
                </div>
              {/each}
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-teal-50 to-teal-100 dark:from-teal-950 dark:to-teal-900 pb-6"
            >
              <CardTitle>📋 Professional Info</CardTitle>
            </CardHeader>
            <CardContent class="pt-6 space-y-4">
              {#if stats.metadata.object.isni}
                <div>
                  <p class="text-sm text-muted-foreground">ISNI</p>
                  <p class="text-lg font-mono">{stats.metadata.object.isni}</p>
                </div>
              {/if}
              {#if stats.metadata.object.ipi}
                <div>
                  <p class="text-sm text-muted-foreground">IPI</p>
                  <p class="text-lg font-mono">{stats.metadata.object.ipi}</p>
                </div>
              {/if}
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>

    <!-- Social Media Stats -->
    <div in:fly={{ y: 20, duration: 400, delay: 400 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500"
        >
          Social Media Performance
        </h2>
      </div>
      {#if stats?.followers}
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-950 dark:to-indigo-900 pb-6"
            >
              <CardTitle>👥 Followers</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.followers.object.followers)}
              </div>
              <p class="text-xs text-muted-foreground">
                Platform: {stats.followers.object.platform}
              </p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-violet-50 to-violet-100 dark:from-violet-950 dark:to-violet-900 pb-6"
            >
              <CardTitle>❤️ Engagement</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.followers.object.engagement)}
              </div>
              <p class="text-xs text-muted-foreground">Total interactions</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-fuchsia-50 to-fuchsia-100 dark:from-fuchsia-950 dark:to-fuchsia-900 pb-6"
            >
              <CardTitle>👀 Total Views</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.followers.object.views)}
              </div>
              <p class="text-xs text-muted-foreground">Across all content</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 pb-6"
            >
              <CardTitle>🔄 Social Activity</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.followers.object.engagement)}
              </div>
              <p class="text-xs text-muted-foreground">Comments, likes & shares</p>
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>

    <!-- Streaming Stats -->
    <div in:fly={{ y: 20, duration: 400, delay: 500 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-cyan-500"
        >
          Streaming Analytics
        </h2>
      </div>
      {#if stats?.streaming}
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 pb-6"
            >
              <CardTitle>🌊 Total Streams</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.streaming.object.streams)}
              </div>
              <p class="text-xs text-muted-foreground">
                Platform: {stats.streaming.object.platform}
              </p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-950 dark:to-cyan-900 pb-6"
            >
              <CardTitle>👥 Monthly Listeners</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.streaming.object.listeners)}
              </div>
              <p class="text-xs text-muted-foreground">Unique listeners</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-teal-50 to-teal-100 dark:from-teal-950 dark:to-teal-900 pb-6"
            >
              <CardTitle>📝 Playlist Inclusions</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.streaming.object.playlists)}
              </div>
              <p class="text-xs text-muted-foreground">Total playlists</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900 pb-6"
            >
              <CardTitle>🤝 Total Engagement</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats.streaming.object.engagement)}
              </div>
              <p class="text-xs text-muted-foreground">Streams & listeners combined</p>
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>
  </div>
</div>
