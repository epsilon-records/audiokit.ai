<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';

  let services = $state([
    {
      title: 'Digital Distribution',
      description: 'Get your music on 200+ platforms including Spotify, Apple Music, and TikTok',
      features: ['Unlimited releases', 'Real-time analytics', 'Monthly payments'],
      icon: '🎵',
      price: 'Starting at $99/year',
      color: 'yellow',
    },
    {
      title: 'Marketing & Promotion',
      description: 'Boost your visibility with targeted campaigns and playlist pitching',
      features: [
        'Playlist submission',
        'Social media promotion',
        'Press coverage',
        'Fan engagement',
      ],
      icon: '🚀',
      price: 'Custom pricing',
      color: 'cyan',
    },
    {
      title: 'Artist Development',
      description: 'Professional guidance to elevate your music career',
      features: ['1-on-1 mentoring', 'Brand development', 'Release strategy', 'Network access'],
      icon: '⭐',
      price: 'From $199/month',
      color: 'green',
    },
    {
      title: 'Analytics & Insights',
      description: 'Deep dive into your performance metrics and audience data',
      features: [
        'Streaming analytics',
        'Audience demographics',
        'Revenue tracking',
        'Trend analysis',
      ],
      icon: '📊',
      price: 'Included free',
      color: 'pink',
    },
  ]);
</script>

<div class="container max-w-6xl mx-auto px-4 py-16 mt-20">
  <!-- Header Section -->
  <div class="text-center mb-16">
    <h1
      class="text-4xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
    >
      Services That Scale Your Success
    </h1>
    <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
      Everything you need to build a successful music career, from distribution to marketing and
      beyond.
    </p>
  </div>

  <!-- Services Grid -->
  <div class="grid md:grid-cols-2 gap-8 mb-16">
    {#each services as service}
      <div
        class={cn(
          'group relative p-8 rounded-lg border border-border/40 transition-all',
          service.color === 'yellow' && 'bg-yellow-100/50 hover:bg-yellow-100/80',
          service.color === 'cyan' && 'bg-cyan-100/50 hover:bg-cyan-100/80',
          service.color === 'green' && 'bg-green-100/50 hover:bg-green-100/80',
          service.color === 'pink' && 'bg-pink-100/50 hover:bg-pink-100/80',
        )}
      >
        <div class="mb-4 text-4xl">{service.icon}</div>
        <h3 class="text-2xl font-bold mb-3">{service.title}</h3>
        <p class="text-muted-foreground mb-6">{service.description}</p>

        <ul class="space-y-3 mb-8">
          {#each service.features as feature}
            <li class="flex items-center gap-2">
              <svg
                class="w-5 h-5 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
              {feature}
            </li>
          {/each}
        </ul>

        <div class="flex items-center justify-between">
          <span class="font-semibold text-lg">{service.price}</span>
          <Button variant="outline">Learn More</Button>
        </div>
      </div>
    {/each}
  </div>

  <!-- CTA Section -->
  <div class="text-center p-12 rounded-lg border border-border/40 bg-neutral-100/50">
    <h2 class="text-3xl font-bold mb-4">Ready to Take Your Music Further?</h2>
    <p class="text-muted-foreground mb-8 max-w-2xl mx-auto">
      Join thousands of artists who are building their careers with our comprehensive suite of
      services.
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <Button size="lg" class="text-lg px-8">Get Started Now</Button>
      <Button size="lg" variant="outline" class="text-lg px-8">Schedule a Call</Button>
    </div>
  </div>
</div>

<!-- Background decoration -->
<div
  class="absolute inset-0 -z-10 h-full w-full bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
></div>
