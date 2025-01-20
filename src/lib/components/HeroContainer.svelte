<script lang="ts">
  import HeroSection from '$lib/components/HeroSection.svelte';
  import { fade } from 'svelte/transition';
</script>

<section
  class="relative min-h-[80vh] flex items-center justify-center overflow-hidden bg-neutral-100"
  in:fade={{ duration: 1000, delay: 200 }}
>
  <div class="relative z-10 w-full">
    <HeroSection />
  </div>
</section>
