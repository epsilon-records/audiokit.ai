<script lang="ts">
  import { fly } from 'svelte/transition';

  interface Props {
    ANIMATION_BASE_DELAY: number;
  }
  let { ANIMATION_BASE_DELAY } = $props<Props>();
</script>

<div in:fly={{ y: 30, duration: 800, delay: ANIMATION_BASE_DELAY }} class="space-y-4">
  <h1
    class="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
  >
    Music Distribution
    <span class="block mt-2">For The API Era</span>
  </h1>

  <p class="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
    Professional music distribution, marketing, and industry services. Built for developers, loved
    by artists, engineered for scale.
  </p>
</div>
