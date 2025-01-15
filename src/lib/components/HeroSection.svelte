<script lang="ts">
  import { Button } from '$lib/components/ui/button';

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
        Turn Your Music Into
        <span class="block mt-2">Your Empire</span>
      </h1>

      <!-- Compelling subheading -->
      <p class="text-lg md:text-xl text-muted-foreground max-w-2xl leading-relaxed">
        Professional music distribution, marketing, and industry services to help independent
        artists reach millions of listeners worldwide.
      </p>

      <!-- CTA buttons -->
      <div class="flex flex-col sm:flex-row gap-4 mt-8">
        <Button size="lg" class="text-lg px-8" href="/sign-up">Start Distribution</Button>
        <Button size="lg" variant="outline" class="text-lg px-8" href="/services"
          >Explore Services</Button
        >
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
