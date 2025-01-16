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

  let stats = $state({
    artists: '40+',
    streams: '500K+',
    countries: '15+',
  });
</script>

<!-- Main content -->
<div class="relative min-h-[600px]">
  <div class="container relative z-10 px-4 max-w-6xl mx-auto">
    <div class="flex flex-col items-center text-center space-y-8">
      <!-- Main heading with gradient -->
      <h1
        class="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
      >
        Music Distribution
        <span class="block mt-2">For The API Era</span>
      </h1>

      <!-- Updated subheading to reinforce the tech-first message -->
      <p class="text-lg md:text-xl text-muted-foreground max-w-2xl leading-relaxed">
        Professional music distribution, marketing, and industry services. Built for developers,
        loved by artists, engineered for scale.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-col sm:flex-row gap-4">
        <Button size="lg" class="text-lg px-8" href="/sign-up">Get Started</Button>
        <Button size="lg" variant="outline" class="text-lg px-8" href="/services">
          Learn More
        </Button>
      </div>

      <!-- Stats section -->
      <div
        class="border-cyan-100 grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-16 mt-16 pt-8 border-t border-border/40 w-full max-w-3xl"
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

      <!-- DSP Logos -->
      <div class="border-cyan-100 border-t border-border/40 mt-16 pt-8 w-full max-w-3xl">
        <p class="text-sm text-muted-foreground mb-6">Available on all major platforms</p>
        <div
          class="grid grid-cols-4 md:grid-cols-6 gap-4 md:gap-6 items-center justify-items-center"
        >
          <!-- Music Platforms -->
          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#1DB954] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siSpotify.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#FA243C] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siApplemusic.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#FF0000] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siYoutubemusic.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#000000] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siTidal.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#FF9900] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siAmazonmusic.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#FF6B00] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siSoundcloud.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#629AA9] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siBandcamp.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#00A4DC] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siPandora.path} />
          </svg>

          <!-- Social Platforms -->
          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#000000] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siTiktok.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#E4405F] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siInstagram.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#000000] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siX.path} />
          </svg>

          <svg
            class="w-10 h-10 md:w-12 md:h-12 text-[#9146FF] hover:scale-110 transition-transform"
            viewBox="0 0 24 24"
          >
            <path fill="currentColor" d={siTwitch.path} />
          </svg>
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
