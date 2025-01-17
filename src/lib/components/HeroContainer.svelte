<script lang="ts">
  import FlickeringGrid from '$lib/components/FlickeringGrid.svelte';
  import { onMount } from 'svelte';
  import HeroSection from '$lib/components/HeroSection.svelte';
  import { fade } from 'svelte/transition';

  let width = $state(1920); // Default fallback
  let height = $state(1080);
  let mounted = $state(false);

  onMount(() => {
    const updateDimensions = () => {
      width = window.innerWidth;
      height = window.innerHeight;
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    mounted = true;

    return () => window.removeEventListener('resize', updateDimensions);
  });
</script>

<section
  class="relative min-h-[80vh] flex items-center justify-center overflow-hidden bg-neutral-100"
  in:fade={{ duration: 1000, delay: 200 }}
>
  {#if mounted}
    <FlickeringGrid
      class="z-0 absolute inset-0 size-full"
      {width}
      {height}
      squareSize={width < 768 ? 10 : 14}
      gridGap={width < 768 ? 12 : 16}
      color="#CFFF04"
      maxOpacity={0.35}
      flickerChance={0.1}
    />
  {/if}

  <div class="relative z-10 w-full">
    <HeroSection />
  </div>
</section>
