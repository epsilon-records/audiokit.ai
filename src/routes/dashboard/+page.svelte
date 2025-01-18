<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { formatNumber } from '$lib/utils/format';
  import { fade, fly } from 'svelte/transition';
  import { AlertCircle } from 'lucide-svelte';
  import { Alert, AlertDescription } from '$lib/components/ui/alert';
  import { Badge } from '$lib/components/ui/badge';

  interface Stats {
    followers: {
      comments: number;
      engagement: number;
      followers: number;
      likes: number;
      shares: number;
      views: number;
      platform: string;
    };
    streaming: {
      streams: number;
      listeners: number;
      playlists: number;
      shares: number;
      views: number;
      timestamp: number;
      platform: string;
    };
  }

  let { data } = $props<{ data: { stats?: Stats; hasActiveSubscription: boolean } }>();

  // Add fake stats when no real stats are available
  let stats = $derived(
    data.stats ?? {
      followers: {
        comments: 0,
        engagement: 0,
        followers: 0,
        likes: 0,
        shares: 0,
        views: 0,
        platform: 'No Platform Connected',
      },
      streaming: {
        streams: 0,
        listeners: 0,
        playlists: 0,
        shares: 0,
        views: 0,
        timestamp: Date.now(),
        platform: 'No Platform Connected',
      },
    }
  );

  let totalSocialEngagement = $derived(
    stats.followers.comments + stats.followers.likes + stats.followers.shares
  );

  let totalStreamingEngagement = $derived(stats.streaming.streams + stats.streaming.listeners);
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Profile</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Manage your artist information, biography, and social media presence.
    </p>

    {#if !data.stats}
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
    <!-- Social Media Stats -->
    <div in:fly={{ y: 20, duration: 400, delay: 300 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500"
        >
          Social Media Performance
        </h2>
      </div>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-950 dark:to-indigo-900 pb-6"
          >
            <CardTitle>Followers</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(stats.followers.followers)}
            </div>
            <p class="text-xs text-muted-foreground">
              Platform: {stats.followers.platform}
            </p>
          </CardContent>
        </Card>

        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-violet-50 to-violet-100 dark:from-violet-950 dark:to-violet-900 pb-6"
          >
            <CardTitle>Engagement</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(stats.followers.engagement)}
            </div>
            <p class="text-xs text-muted-foreground">Total interactions</p>
          </CardContent>
        </Card>

        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-fuchsia-50 to-fuchsia-100 dark:from-fuchsia-950 dark:to-fuchsia-900 pb-6"
          >
            <CardTitle>Total Views</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(stats.followers.views)}
            </div>
            <p class="text-xs text-muted-foreground">Across all content</p>
          </CardContent>
        </Card>

        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 pb-6"
          >
            <CardTitle>Social Activity</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(totalSocialEngagement)}
            </div>
            <p class="text-xs text-muted-foreground">Comments, likes & shares</p>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Streaming Stats -->
    <div in:fly={{ y: 20, duration: 400, delay: 400 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-cyan-500"
        >
          Streaming Analytics
        </h2>
      </div>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 pb-6"
          >
            <CardTitle>Total Streams</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(stats.streaming.streams)}
            </div>
            <p class="text-xs text-muted-foreground">
              Platform: {stats.streaming.platform}
            </p>
          </CardContent>
        </Card>

        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-950 dark:to-cyan-900 pb-6"
          >
            <CardTitle>Monthly Listeners</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(stats.streaming.listeners)}
            </div>
            <p class="text-xs text-muted-foreground">Unique listeners</p>
          </CardContent>
        </Card>

        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-teal-50 to-teal-100 dark:from-teal-950 dark:to-teal-900 pb-6"
          >
            <CardTitle>Playlist Inclusions</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(stats.streaming.playlists)}
            </div>
            <p class="text-xs text-muted-foreground">Total playlists</p>
          </CardContent>
        </Card>

        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900 pb-6"
          >
            <CardTitle>Total Engagement</CardTitle>
          </CardHeader>
          <CardContent class="pt-6">
            <div class="text-2xl font-bold">
              {formatNumber(totalStreamingEngagement)}
            </div>
            <p class="text-xs text-muted-foreground">Streams & listeners combined</p>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</div>
