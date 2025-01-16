<script lang="ts">
  import { fly } from 'svelte/transition';

  interface Props {
    ANIMATION_BASE_DELAY: number;
  }
  const { ANIMATION_BASE_DELAY } = $props<Props>();

  let stats = $state({
    artists: '40+',
    streams: '500K+',
    tracks: '120+',
  });
</script>

<div
  in:fly={{ y: 30, duration: 800, delay: ANIMATION_BASE_DELAY + 400 }}
  class="grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-16 mt-8 pt-8 border-t border-border/40 w-full max-w-3xl"
>
  {#each Object.entries(stats) as [key, value]}
    <div class="flex flex-col items-center">
      <span
        class="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
      >
        {value}
      </span>
      <span class="text-sm text-muted-foreground mt-2 capitalize">
        {key.replace('_', ' ')}
      </span>
    </div>
  {/each}
</div>
