<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { formatNumber } from '$lib/utils/format';

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

  // Derived calculations for total engagement
  let totalSocialEngagement = $derived(
    data.stats
      ? data.stats.followers.comments + data.stats.followers.likes + data.stats.followers.shares
      : 0
  );

  let totalStreamingEngagement = $derived(
    data.stats ? data.stats.streaming.streams + data.stats.streaming.listeners : 0
  );
</script>

{#if !data.stats}
  <div class="flex flex-col items-center justify-center min-h-[50vh] gap-4">
    <h2 class="text-2xl font-semibold">No Stats Available</h2>
    <p class="text-muted-foreground">
      We couldn't find any statistics for your artist profile. Please ensure your artist name is
      correctly set up.
    </p>
  </div>
{:else}
  <div class="space-y-8">
    <!-- Social Media Stats -->
    <div class="space-y-4">
      <h2 class="text-2xl font-semibold">Social Media Performance</h2>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Followers</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(data.stats.followers.followers)}
            </div>
            <p class="text-xs text-muted-foreground">
              Platform: {data.stats.followers.platform}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Engagement</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(data.stats.followers.engagement)}
            </div>
            <p class="text-xs text-muted-foreground">Total interactions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Views</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(data.stats.followers.views)}
            </div>
            <p class="text-xs text-muted-foreground">Across all content</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Social Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(totalSocialEngagement)}
            </div>
            <p class="text-xs text-muted-foreground">Comments, likes & shares</p>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Streaming Stats -->
    <div class="space-y-4">
      <h2 class="text-2xl font-semibold">Streaming Analytics</h2>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Streams</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(data.stats.streaming.streams)}
            </div>
            <p class="text-xs text-muted-foreground">
              Platform: {data.stats.streaming.platform}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monthly Listeners</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(data.stats.streaming.listeners)}
            </div>
            <p class="text-xs text-muted-foreground">Unique listeners</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Playlist Inclusions</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(data.stats.streaming.playlists)}
            </div>
            <p class="text-xs text-muted-foreground">Total playlists</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Engagement</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-2xl font-bold">
              {formatNumber(totalStreamingEngagement)}
            </div>
            <p class="text-xs text-muted-foreground">Streams & listeners combined</p>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
{/if}
