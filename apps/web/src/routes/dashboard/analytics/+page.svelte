<script lang="ts">
  import { fly } from 'svelte/transition';
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { formatNumber } from '$lib/utils/format';
  import type { Artist } from '$lib/types';
  import Chart from 'chart.js/auto';

  let { data } = $props();
  let artist: Artist = $derived(data.artist);
  let followers = $derived.by(
    () =>
      (artist?.followers as {
        spotify: number;
        instagram?: number;
        twitter?: number;
        facebook?: number;
      }) ?? {}
  );
  let streaming = $derived.by(
    () => (artist?.streaming as { spotify: { items: { date: string; value: number }[] } }) ?? {}
  );

  let streamingChartCanvas: HTMLCanvasElement;
  let streamingChart: Chart;

  let followersChartCanvas: HTMLCanvasElement;
  let followersChart: Chart;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
    },
  };

  $effect(() => {
    if (streaming.spotify?.items) {
      const labels = streaming.spotify.items.map((item) =>
        new Date(item.date).toLocaleDateString()
      );
      const data = streaming.spotify.items.map((item) => item.value);

      streamingChart = new Chart(streamingChartCanvas, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Spotify Listeners',
              data,
              borderColor: '#1DB954',
              backgroundColor: 'rgba(29, 185, 84, 0.1)',
              borderWidth: 2,
              tension: 0.2,
              pointRadius: 0,
            },
          ],
        },
        options: chartOptions,
      });
    }
  });

  $effect(() => {
    if (followers) {
      const labels = Object.keys(followers);
      const data = Object.values(followers);

      followersChart = new Chart(followersChartCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: 'Social Media Followers',
              data,
              backgroundColor: [
                'rgba(29, 185, 84, 0.8)', // Spotify
                'rgba(131, 58, 180, 0.8)', // Instagram
                'rgba(29, 161, 242, 0.8)', // Twitter
                'rgba(66, 103, 178, 0.8)', // Facebook
              ],
              borderRadius: 5,
              barPercentage: 0.8,
              categoryPercentage: 0.8,
            },
          ],
        },
        options: {
          ...chartOptions,
          scales: {
            ...chartOptions.scales,
            x: {
              ...chartOptions.scales.x,
              grid: {
                display: false,
              },
              offset: true,
            },
          },
        },
      });
    }
  });
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Analytics</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Gain valuable insights into your streaming performance, audience engagement, and revenue
      trends.
    </p>
  </div>
  <div class="space-y-8">
    <!-- Streaming Stats -->
    <div in:fly={{ y: 20, duration: 400, delay: 700 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-cyan-500"
        >
          Streaming Analytics
        </h2>
      </div>
      {#if artist?.streaming}
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#1DB954] to-[#1ed760] dark:from-[#1DB954]/30 dark:to-[#1ed760]/30 pb-6"
            >
              <CardTitle class="flex items-center gap-2">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"
                  />
                </svg>
                Current Listeners
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(streaming.spotify.items[streaming.spotify.items.length - 1].value)}
              </div>
              <p class="text-xs text-muted-foreground">
                As of {new Date(
                  streaming.spotify.items[streaming.spotify.items.length - 1].date
                ).toLocaleDateString()}
              </p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#1DB954] to-[#1ed760] dark:from-[#1DB954]/30 dark:to-[#1ed760]/30 pb-6"
            >
              <CardTitle>📈 30-Day Peak</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(
                  Math.max(...streaming?.spotify?.items.slice(-30).map((item: any) => item.value))
                )}
              </div>
              <p class="text-xs text-muted-foreground">Highest in last 30 days</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#1DB954] to-[#1ed760] dark:from-[#1DB954]/30 dark:to-[#1ed760]/30 pb-6"
            >
              <CardTitle>📊 30-Day Average</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(
                  Math.round(
                    streaming.spotify.items
                      .slice(-30)
                      .reduce((acc: number, item: any) => acc + item.value, 0) / 30
                  )
                )}
              </div>
              <p class="text-xs text-muted-foreground">Average over last 30 days</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#1DB954] to-[#1ed760] dark:from-[#1DB954]/30 dark:to-[#1ed760]/30 pb-6"
            >
              <CardTitle>📱 Trend</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              {#if streaming.spotify.items.length >= 2}
                {@const lastValue =
                  streaming.spotify.items[streaming.spotify.items.length - 1].value}
                {@const prevValue =
                  streaming.spotify.items[streaming.spotify.items.length - 2].value}
                {@const change = ((lastValue - prevValue) / prevValue) * 100}
                <div class="text-2xl font-bold flex items-center gap-2">
                  <span class={change >= 0 ? 'text-green-600' : 'text-red-600'}>
                    {change >= 0 ? '+' : ''}{change.toFixed(1)}%
                  </span>
                </div>
                <p class="text-xs text-muted-foreground">Daily change</p>
              {/if}
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>

    <!-- Streaming Chart -->
    <div in:fly={{ y: 20, duration: 400, delay: 500 }} class="space-y-4">
      <h2
        class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-cyan-500"
      >
        Spotify Listeners Over Time
      </h2>
      <Card>
        <CardContent class="h-96">
          <canvas bind:this={streamingChartCanvas}></canvas>
        </CardContent>
      </Card>
    </div>

    <!-- Social Media Stats -->
    <div in:fly={{ y: 20, duration: 400, delay: 400 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500"
        >
          Social Media Analytics
        </h2>
      </div>
      {#if artist?.followers}
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#1DB954] to-[#1ed760] dark:from-[#1DB954]/30 dark:to-[#1ed760]/30 pb-6"
            >
              <CardTitle class="flex items-center gap-2">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"
                  />
                </svg>
                Spotify
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(followers.spotify)}
              </div>
              <p class="text-xs text-muted-foreground">Followers</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#833AB4] to-[#E1306C] dark:from-[#833AB4]/30 dark:to-[#E1306C]/30 pb-6"
            >
              <CardTitle class="flex items-center gap-2">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"
                  />
                </svg>
                Instagram
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(followers.instagram)}
              </div>
              <p class="text-xs text-muted-foreground">Followers</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#1DA1F2] to-[#1a91da] dark:from-[#1DA1F2]/30 dark:to-[#1a91da]/30 pb-6"
            >
              <CardTitle class="flex items-center gap-2">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"
                  />
                </svg>
                X (Twitter)
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(followers.twitter)}
              </div>
              <p class="text-xs text-muted-foreground">Followers</p>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-[#4267B2] to-[#385898] dark:from-[#4267B2]/30 dark:to-[#385898]/30 pb-6"
            >
              <CardTitle class="flex items-center gap-2">
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path
                    d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
                  />
                </svg>
                Facebook
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(followers.facebook)}
              </div>
              <p class="text-xs text-muted-foreground">Followers</p>
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>

    <!-- Social Media Followers Chart -->
    <div in:fly={{ y: 20, duration: 400, delay: 600 }} class="space-y-4">
      <h2
        class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500"
      >
        Social Media Followers
      </h2>
      <Card>
        <CardContent class="h-96">
          <canvas bind:this={followersChartCanvas}></canvas>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
