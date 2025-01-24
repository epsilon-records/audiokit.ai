<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { fly } from 'svelte/transition';
  import { AlertCircle } from 'lucide-svelte';
  import { Badge } from '$lib/components/ui/badge';
  import { formatNumber } from '$lib/utils/format';

  // Use $props with the interface
  let { data } = $props();

  // Use $derived for reactive values
  let user = $derived(data.user);
  let org = $derived(data.org);
  let stats = $derived(data.stats);
  let tracks = $derived(data.tracks);
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Overview</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Get insights into your performance metrics and manage your artist profile.
    </p>
    {#if !stats?.metadata}
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
                  <p class="text-sm text-muted-foreground">Organization</p>
                  <p class="text-lg font-semibold">{org.name}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Slug</p>
                  <p class="text-base font-semibold">@{org.slug}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Team Members</p>
                  <p class="text-base">
                    {org.membersCount || 1} / {org.maxAllowedMemberships}
                  </p>
                </div>
              </div>
              <div class="flex justify-center items-center pr-8">
                <div class="w-48 h-48 m-4 flex-shrink-0">
                  <img
                    src={org.imageUrl}
                    alt="Organization"
                    class="w-full border-black border-2 h-full rounded-full object-cover"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900 pb-6"
            >
              <CardTitle>🎵 Catalog</CardTitle>
            </CardHeader>
            <CardContent class="pt-6 space-y-4">
              <div>
                <p class="text-sm text-muted-foreground">Tracks Released</p>
                <p class="text-2xl font-bold">{formatNumber(tracks?.items.length ?? 0)}</p>
              </div>
              {#each stats?.metadata.genres as genre}
                <div class="mb-4">
                  <p class="text-lg font-semibold capitalize">{genre.root}</p>
                  {#if genre.sub && genre.sub.length > 0}
                    <div class="flex flex-wrap gap-2 mt-2">
                      {#each genre.sub as subGenre}
                        <Badge
                          variant="secondary"
                          class="capitalize hover:bg-emerald-100 dark:hover:bg-emerald-800 transition-colors"
                        >
                          {subGenre}
                        </Badge>
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
              <div>
                <p class="text-sm text-muted-foreground">ISNI</p>
                <p class="text-lg font-mono">{stats?.metadata?.object?.isni ?? 'Unknown'}</p>
              </div>

              <div>
                <p class="text-sm text-muted-foreground">IPI</p>
                <p class="text-lg font-mono">{stats?.metadata?.object?.ipi ?? 'Unknown'}</p>
              </div>

              <div>
                <p class="text-sm text-muted-foreground">Updated At</p>
                <p class="text-lg font-semibold">
                  {new Date(org.updatedAt).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p class="text-sm text-muted-foreground">Member Since</p>
                <p class="text-lg font-semibold">
                  {new Date(org.createdAt).toLocaleDateString()}
                </p>
              </div>
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
                {formatNumber(stats?.followers.spotify)}
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
                    d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"
                  />
                </svg>
                Instagram
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(stats?.followers.instagram)}
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
                {formatNumber(stats?.followers.twitter)}
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
                {formatNumber(stats?.followers.facebook)}
              </div>
              <p class="text-xs text-muted-foreground">Followers</p>
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
                {formatNumber(
                  stats?.streaming.spotify.items[stats?.streaming.spotify.items.length - 1].value
                )}
              </div>
              <p class="text-xs text-muted-foreground">
                As of {new Date(
                  stats?.streaming.spotify.items[stats?.streaming.spotify.items.length - 1].date
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
                  Math.max(...stats?.streaming.spotify.items.slice(-30).map((item) => item.value))
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
                    stats?.streaming.spotify.items
                      .slice(-30)
                      .reduce((acc, item) => acc + item.value, 0) / 30
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
              {#if stats?.streaming.spotify.items.length >= 2}
                {@const lastValue =
                  stats?.streaming.spotify.items[stats?.streaming.spotify.items.length - 1].value}
                {@const prevValue =
                  stats?.streaming.spotify.items[stats?.streaming.spotify.items.length - 2].value}
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

    <!-- Artist & Repertoire -->
    <div in:fly={{ y: 20, duration: 400, delay: 350 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-indigo-500"
        >
          Artist & Repertoire
        </h2>
      </div>
      {#if user}
        <div class="grid gap-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 pb-6"
            >
              <CardTitle>👔 A&R Details</CardTitle>
            </CardHeader>
            <CardContent class="pt-6 space-y-4 flex justify-between">
              <div class="flex-1 space-y-4">
                <div>
                  <p class="text-sm text-muted-foreground">Name</p>
                  <p class="text-lg font-semibold">{user.firstName} {user.lastName}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Username</p>
                  <p class="text-lg font-semibold">@{user.username}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Contact</p>
                  {#each user.emailAddresses as email}
                    <p class="text-base">{email}</p>
                  {/each}
                  {#each user.phoneNumbers as phone}
                    <p class="text-base">{phone}</p>
                  {/each}
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Last Active</p>
                  {#if user.lastActiveAt}
                    <p class="text-base">{new Date(user.lastActiveAt).toLocaleDateString()}</p>
                  {/if}
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Joined</p>
                  <p class="text-base">{new Date(user.createdAt).toLocaleDateString()}</p>
                </div>
              </div>
              <div class="flex justify-center items-center pr-8">
                <div class="w-48 h-48 m-4 flex-shrink-0">
                  <img
                    src={user.imageUrl}
                    alt="A&R Representative"
                    class="w-full h-full rounded-full object-cover border-2 border-black"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>
  </div>
</div>
