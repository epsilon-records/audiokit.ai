<script lang="ts">
  import { ChartBarSquare, Users, Heart, CurrencyDollar } from 'svelte-hero-icons';
  import StatWidget from '$lib/components/dashboard/StatWidget.svelte';
  import { fade } from 'svelte/transition';

  let { data } = $props();

  const platformStats = $derived({
    spotify: {
      monthly_listeners: 45892,
      top_tracks: 12,
      playlist_adds: 892,
      change: 12.4,
    },
    appleMusic: {
      plays: 12453,
      playlist_adds: 234,
      change: 8.2,
    },
    soundcloud: {
      plays: 23412,
      followers: 1234,
      change: -2.1,
    },
  });

  const socialStats = $derived({
    instagram: data?.stats?.instagramFollowers || 0,
    tiktok: 25600,
    youtube: 12300,
    twitter: 8900,
  });

  const engagementRate = $derived(data?.stats?.engagementRate || 0);
  const weeklyGrowth = $derived(data?.stats?.weeklyGrowth || 0);
</script>

<div class="container mx-auto px-4 py-8">
  {#if !data.hasActiveSubscription}
    <div class="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-8 rounded" in:fade>
      <p class="text-yellow-700">
        <span class="font-bold">Limited Access:</span>
        Upgrade to Pro to unlock full analytics and insights.
      </p>
    </div>
  {/if}

  <!-- Overview Stats -->
  <section class="mb-12">
    <h2
      class="text-2xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
    >
      Performance Overview
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatWidget
        title="Total Followers"
        value={Object.values(socialStats).reduce((a, b) => a + b, 0)}
        change={weeklyGrowth}
        icon={Users}
      />
      <StatWidget title="Engagement Rate" value={engagementRate} change={1.2} icon={Heart} />
      <StatWidget
        title="Monthly Listeners"
        value={platformStats.spotify.monthly_listeners}
        change={platformStats.spotify.change}
        icon={ChartBarSquare}
      />
      <StatWidget title="Revenue Growth" value={12500} change={15.7} icon={CurrencyDollar} />
    </div>
  </section>

  <!-- Platform Performance -->
  <section class="mb-12">
    <h2 class="text-2xl font-bold mb-6">Platform Performance</h2>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Spotify -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-lg">Spotify</h3>
          <span class={platformStats.spotify.change > 0 ? 'text-green-500' : 'text-red-500'}>
            {platformStats.spotify.change > 0 ? '+' : ''}{platformStats.spotify.change}%
          </span>
        </div>
        <div class="space-y-4">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Monthly Listeners</span>
            <span class="font-medium"
              >{platformStats.spotify.monthly_listeners.toLocaleString()}</span
            >
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Top Tracks</span>
            <span class="font-medium">{platformStats.spotify.top_tracks}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Playlist Adds</span>
            <span class="font-medium">{platformStats.spotify.playlist_adds}</span>
          </div>
        </div>
      </div>

      <!-- Apple Music -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-lg">Apple Music</h3>
          <span class={platformStats.appleMusic.change > 0 ? 'text-green-500' : 'text-red-500'}>
            {platformStats.appleMusic.change > 0 ? '+' : ''}{platformStats.appleMusic.change}%
          </span>
        </div>
        <div class="space-y-4">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Total Plays</span>
            <span class="font-medium">{platformStats.appleMusic.plays.toLocaleString()}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Playlist Adds</span>
            <span class="font-medium">{platformStats.appleMusic.playlist_adds}</span>
          </div>
        </div>
      </div>

      <!-- SoundCloud -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-lg">SoundCloud</h3>
          <span class={platformStats.soundcloud.change > 0 ? 'text-green-500' : 'text-red-500'}>
            {platformStats.soundcloud.change > 0 ? '+' : ''}{platformStats.soundcloud.change}%
          </span>
        </div>
        <div class="space-y-4">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Total Plays</span>
            <span class="font-medium">{platformStats.soundcloud.plays.toLocaleString()}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Followers</span>
            <span class="font-medium">{platformStats.soundcloud.followers.toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Social Media Performance -->
  <section>
    <h2 class="text-2xl font-bold mb-6">Social Media Reach</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {#each Object.entries(socialStats) as [platform, followers]}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h3 class="font-semibold text-lg capitalize mb-2">{platform}</h3>
          <div class="flex items-end gap-2">
            <span class="text-2xl font-bold">
              {followers.toLocaleString()}
            </span>
            <span class="text-gray-600 dark:text-gray-400 text-sm">followers</span>
          </div>
        </div>
      {/each}
    </div>
  </section>
</div>
