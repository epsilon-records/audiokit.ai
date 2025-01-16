<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import {
    siSpotify,
    siApplemusic,
    siYoutubemusic,
    siSoundcloud,
    siBandcamp,
    siTidal,
    siAmazonmusic,
    siPandora,
    siTiktok,
    siInstagram,
    siX,
    siTwitch,
  } from 'simple-icons';
  import { fly, fade } from 'svelte/transition';

  let stats = $state({
    artists: '40+',
    streams: '500K+',
    tracks: '120+',
  });

  const ANIMATION_BASE_DELAY = 400;
</script>

<div class="relative px-4 py-12 md:py-24">
  <div class="container relative z-10 max-w-6xl mx-auto">
    <div class="flex flex-col items-center text-center space-y-8 md:space-y-12">
      <!-- Main heading -->
      <div in:fly={{ y: 30, duration: 800, delay: ANIMATION_BASE_DELAY }} class="space-y-4">
        <h1
          class="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
        >
          Music Distribution
          <span class="block mt-2">For The API Era</span>
        </h1>

        <p class="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          Professional music distribution, marketing, and industry services. Built for developers,
          loved by artists, engineered for scale.
        </p>
      </div>

      <!-- CTA Buttons -->
      <div
        in:fly={{ y: 30, duration: 800, delay: ANIMATION_BASE_DELAY + 200 }}
        class="flex flex-col sm:flex-row gap-4"
      >
        <Button size="lg" class="text-lg px-8" href="/sign-up">Get Started</Button>
        <Button size="lg" variant="outline" class="text-lg px-8" href="/services">
          Learn More
        </Button>
      </div>

      <!-- Stats section -->
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

      <!-- Platform Logos -->
      <div
        in:fade={{ duration: 1000, delay: ANIMATION_BASE_DELAY + 600 }}
        class="w-full max-w-3xl space-y-6 pt-8 border-t border-border/40"
      >
        <p class="text-sm text-muted-foreground">Available on all major platforms</p>
        <div
          class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4 md:gap-6 items-center justify-items-center"
        >
          {#each [{ icon: siSpotify, color: '#1DB954' }, { icon: siApplemusic, color: '#FA243C' }, { icon: siYoutubemusic, color: '#FF0000' }, { icon: siTidal, color: '#000000' }, { icon: siAmazonmusic, color: '#FF9900' }, { icon: siSoundcloud, color: '#FF6B00' }, { icon: siBandcamp, color: '#629AA9' }, { icon: siPandora, color: '#00A4DC' }, { icon: siTiktok, color: '#000000' }, { icon: siInstagram, color: '#E4405F' }, { icon: siX, color: '#000000' }, { icon: siTwitch, color: '#9146FF' }] as item}
            <svg
              class="w-8 h-8 md:w-10 md:h-10 transition-all duration-300 hover:scale-110"
              style="color: {item.color}"
              viewBox="0 0 24 24"
            >
              <path fill="currentColor" d={item.icon.path} />
            </svg>
          {/each}
        </div>
      </div>
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
