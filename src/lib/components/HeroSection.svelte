<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import MainHeading from './hero/MainHeading.svelte';
  import CtaButtons from './hero/CtaButtons.svelte';
  import TechStack from './hero/TechStack.svelte';
  import PlatformLogos from './hero/PlatformLogos.svelte';
  import Stats from './hero/Stats.svelte';

  const ANIMATION_BASE_DELAY = 400;
</script>

<div class="relative px-4 py-12 md:py-24">
  <div
    class="absolute inset-0 z-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>
  <div class="container relative z-10 max-w-6xl mx-auto">
    <div class="flex flex-col items-center text-center space-y-4 md:space-y-8">
      <MainHeading {ANIMATION_BASE_DELAY} />
      <CtaButtons {ANIMATION_BASE_DELAY} />
      <TechStack {ANIMATION_BASE_DELAY} />
      <PlatformLogos {ANIMATION_BASE_DELAY} />
      <!-- <Stats {ANIMATION_BASE_DELAY} /> -->
    </div>
  </div>
</div>

<style>
  @keyframes pulse {
    50% {
      opacity: 0.5;
    }
  }
</style>
