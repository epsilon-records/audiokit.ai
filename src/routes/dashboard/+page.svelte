<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
  import { fly } from 'svelte/transition';
  import { AlertCircle } from 'lucide-svelte';
  import { Badge } from '$lib/components/ui/badge';
  import { formatNumber } from '$lib/utils/format';
  import type { Artist } from '$lib/types';
  import { getServiceIcon } from '$lib/utils/services';

  let { data } = $props();

  let user = $derived(data.user);
  let org = $derived(data.org);
  let artist: Artist = $derived(data.artist);
  let metadata = $derived.by(() => (artist?.metadata as { isni?: string; ipi?: string }) ?? {});
  let services = $derived(data.artist?.services ?? {});
  let genres = $derived.by(
    () => (artist?.metadata as { genres: { root: string; sub: string[] }[] })?.genres ?? []
  );
  let tracks = $derived.by(() => (artist?.tracks as { items: unknown[] })?.items ?? []);
</script>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-4xl font-bold tracking-tight">Artist Overview</h1>

    <p class="mt-2 text-lg text-muted-foreground">
      View your artist details, connected services, and A&R representative information.
    </p>
    {#if !artist?.metadata}
      <div class="mt-4" in:fly={{ y: 20, duration: 400, delay: 200 }}>
        <Badge
          variant="outline"
          class="bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800"
        >
          <AlertCircle class="h-4 w-4 mr-2" />
          Complete your artist profile to unlock powerful features and analytics.
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
      {#if artist?.metadata}
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
                <p class="text-2xl font-bold">
                  {formatNumber(tracks.length)}
                </p>
              </div>
              {#each genres as genre}
                <div class="mb-4">
                  <p class="text-sm text-muted-foreground">Genres</p>
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
                <p class="text-lg font-mono">{metadata.isni || 'Unknown'}</p>
              </div>

              <div>
                <p class="text-sm text-muted-foreground">IPI</p>
                <p class="text-lg font-mono">{metadata.ipi || 'Unknown'}</p>
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

    <!-- Services -->
    <div in:fly={{ y: 20, duration: 400, delay: 600 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-violet-500"
        >
          Services
        </h2>
      </div>
      {#if Object.keys(services).length > 0}
        <Card class="transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
          <CardHeader
            class="bg-gradient-to-br from-pink-50 to-violet-100 dark:from-pink-900/30 dark:to-violet-900/30 pb-6"
          >
            <CardTitle>Connected Services</CardTitle>
          </CardHeader>
          <CardContent class="pt-6 space-y-4">
            <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {#each Object.entries(services).sort( ([a], [b]) => a.localeCompare(b) ) as [service, url]}
                <a
                  href={url.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center gap-2 p-2 rounded-md hover:bg-muted transition-colors"
                >
                  {@html getServiceIcon(service)}
                  <span class="capitalize">{service.replace(/([a-z])([A-Z])/g, '$1 $2')}</span>
                </a>
              {/each}
            </div>
          </CardContent>
        </Card>
      {:else}
        <p class="text-muted-foreground">No platforms connected yet.</p>
      {/if}
    </div>

    <!-- Artist & Repertoire -->
    <div in:fly={{ y: 20, duration: 400, delay: 350 }} class="space-y-4">
      <div class="flex items-center justify-between">
        <h2
          class="text-2xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-indigo-500"
        >
          Artist Representative
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
