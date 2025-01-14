<script lang="ts">
  import FlickeringGrid from '$lib/components/FlickeringGrid.svelte';
  import { onMount } from 'svelte';
  import HeroSection from '$lib/components/HeroSection.svelte';

  let width = 1920; // Default fallback
  let height = 1080;

  onMount(() => {
    const updateDimensions = () => {
      width = window.innerWidth;
      height = window.innerHeight;
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);

    return () => window.removeEventListener('resize', updateDimensions);
  });
</script>

<section class="relative h-screen flex items-center justify-center overflow-hidden bg-black">
  <FlickeringGrid
    class="z-0 absolute inset-0 size-full"
    {width}
    {height}
    squareSize={14}
    gridGap={16}
    color="#ffd700"
    maxOpacity={0.35}
    flickerChance={0.1}
  />

  <HeroSection />
</section>
