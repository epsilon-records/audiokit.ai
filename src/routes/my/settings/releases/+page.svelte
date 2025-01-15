<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { cn } from '$lib/utils';

  let { data } = $props();
</script>

<SettingsContainer title="Manage Releases">
  <svelte:fragment slot="description">Manage your artist releases.</svelte:fragment>
  <div class="space-y-4 bg-white rounded-lg border border-gray-200 p-6">
    {#if data.releases.length === 0}
      <div class="text-center py-6 text-muted-foreground">
        <p>No releases found. Create your first release to get started.</p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each data.releases as release}
          <div
            class="flex flex-col bg-card rounded-lg border shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="aspect-square relative">
              <img
                src={release.cover_artwork[0] || '/images/placeholder-release.jpg'}
                alt={release.release_title}
                class="object-cover w-full h-full rounded-t-lg"
              />
            </div>
            <div class="p-4 space-y-2">
              <h3 class="font-semibold truncate">{release.release_title}</h3>
              <p class="text-sm text-muted-foreground">{release.release_date}</p>
              <div class="flex justify-between items-center mt-4">
                <span
                  class={cn(
                    'px-2 py-1 text-xs rounded-full',
                    release.status === 'published'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800',
                  )}
                >
                  {release.status}
                </span>
                <button
                  class="text-sm text-primary hover:underline"
                  on:click={() => goto(`/my/settings/releases/${release.id}`)}
                >
                  Edit
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</SettingsContainer>
