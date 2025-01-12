<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import FlickeringGrid from "$lib/components/ui/FlickeringGrid.svelte";
  import { onMount } from 'svelte';
  import Nav from "$lib/components/ui/Nav.svelte";

  let width = 1920;  // Default fallback
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

    
    <div class="container relative z-10 px-4 flex flex-col items-center text-center">
    <h1 class="text-white text-4xl md:text-6xl lg:text-7xl font-mono font-bold tracking-tighter mb-6">
      EPSILON RECORDS
    </h1>
    <p class="text-lg md:text-xl text-neutral-400 mb-8 max-w-2xl">
        Underground acid techno label pushing boundaries since 2015
    </p>
    <Button variant="outline" class="border-green-400 bg-green-400 hover:bg-green-300 text-black hover:text-black hover:border-green-300 transition-colors">
        Listen to Latest Release
    </Button>
    </div>
</section>



    
