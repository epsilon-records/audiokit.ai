<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { fly } from 'svelte/transition';
  import { AlertCircle } from 'lucide-svelte';
  import { Badge } from '$lib/components/ui/badge';
  import { formatNumber } from '$lib/utils/format';
  import { getUser, getOrg } from '$lib/server/auth';
  let { data } = $props();

  // Using $derived to maintain reactivity
  let { auth, metadata, streaming, followers } = $derived(data);
  let user = $derived.by(async () => {
    const authData = await auth;
    return await getUser(authData.userId);
  });
  let org = $derived.by(async () => {
    const authData = await auth;
    return await getOrg(authData.orgId);
  });
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Overview</h1>
    <p class="mt-2 text-lg text-muted-foreground">
      Get insights into your performance metrics and manage your artist profile.
    </p>
    {#if !metadata}
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
      {#if metadata}
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
                  <p class="text-lg font-semibold">{auth.org.name}</p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Members</p>
                  <p class="text-base">
                    {auth.org.membersCount} / {auth.org.maxAllowedMemberships}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-muted-foreground">Slug</p>
                  <p class="text-base">@{org.slug}</p>
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
              <CardTitle>🎵 Genres</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              {#each metadata.genres as genre}
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
              {#if metadata.isni}
                <div>
                  <p class="text-sm text-muted-foreground">ISNI</p>
                  <p class="text-lg font-mono">{metadata.isni}</p>
                </div>
              {/if}
              {#if metadata.ipi}
                <div>
                  <p class="text-sm text-muted-foreground">IPI</p>
                  <p class="text-lg font-mono">{metadata.ipi}</p>
                </div>
              {/if}
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

    <!-- Artist & Repertoire -->
    <div in:fly={{ y: 20, duration: 400, delay: 350 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-indigo-500"
        >
          Artist & Repertoire
        </h2>
      </div>
      {#if metadata}
        <div class="grid gap-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 pb-6"
            >
              <CardTitle>👔 A&R Details</CardTitle>
            </CardHeader>
            <CardContent class="pt-6 space-y-4">
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
                <p class="text-base">{user.email}</p>
                {#if user.phone}
                  <p class="text-base">{user.phone}</p>
                {/if}
              </div>
              <div>
                <p class="text-sm text-muted-foreground">Last Sign In</p>
                <p class="text-base">{new Date(user.lastSignedInAt).toLocaleDateString()}</p>
              </div>
              <div class="flex justify-center">
                <img
                  src={user.imageUrl}
                  alt="A&R Representative"
                  class="w-24 h-24 rounded-full object-cover border-2 border-black"
                />
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
      {#if followers}
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-950 dark:to-indigo-900 pb-6"
            >
              <CardTitle>👥 Followers</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(followers.followers)}
              </div>
              <p class="text-xs text-muted-foreground">
                Platform: {followers.platform}
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
                {formatNumber(followers.engagement)}
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
                {formatNumber(followers.views)}
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
                {formatNumber(followers.engagement)}
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
      {#if streaming}
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
            <CardHeader
              class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 pb-6"
            >
              <CardTitle>🌊 Total Streams</CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <div class="text-2xl font-bold">
                {formatNumber(streaming.streams)}
              </div>
              <p class="text-xs text-muted-foreground">
                Platform: {streaming.platform}
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
                {formatNumber(streaming.listeners)}
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
                {formatNumber(streaming.playlists)}
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
                {formatNumber(streaming.engagement)}
              </div>
              <p class="text-xs text-muted-foreground">Streams & listeners combined</p>
            </CardContent>
          </Card>
        </div>
      {/if}
    </div>
  </div>
</div>
