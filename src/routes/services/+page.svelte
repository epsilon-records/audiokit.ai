<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';

  let services = $state([
    {
      title: 'Digital Distribution',
      description: 'Get your music on 200+ platforms',
      features: ['Unlimited releases', 'Real-time analytics', 'Monthly payments'],
      icon: '🎵',
      price: '$99/year',
      color: 'yellow',
    },
    {
      title: 'Marketing & Promotion',
      description: 'Boost your visibility with targeted campaigns',
      features: ['Playlist pitching', 'Social media', 'Press coverage'],
      icon: '🚀',
      price: '$199/release',
      color: 'cyan',
    },
    {
      title: 'Artist Development',
      description: 'Professional guidance for your career',
      features: ['1-on-1 mentoring', 'Brand development', 'Release strategy'],
      icon: '⭐',
      price: 'Custom',
      color: 'green',
    },
    {
      title: 'Analytics & Insights',
      description: 'Deep dive into your performance metrics',
      features: ['Streaming data', 'Audience stats', 'Revenue tracking'],
      icon: '📊',
      price: 'Free',
      color: 'pink',
    },
  ]);
</script>

<div class="container max-w-6xl mx-auto px-4 py-8">
  <div class="text-center mb-8">
    <h1
      class="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-500"
    >
      Services That Scale
    </h1>
    <p class="text-muted-foreground max-w-2xl mx-auto">
      Everything you need to build a successful music career.
    </p>
  </div>

  <div class="grid md:grid-cols-2 gap-6 mb-12">
    {#each services as service}
      <div
        class={cn(
          'group p-6 rounded-lg border border-border/40 transition-all',
          service.color === 'yellow' && 'bg-yellow-100/50 hover:bg-yellow-100/80',
          service.color === 'cyan' && 'bg-cyan-100/50 hover:bg-cyan-100/80',
          service.color === 'green' && 'bg-green-100/50 hover:bg-green-100/80',
          service.color === 'pink' && 'bg-pink-100/50 hover:bg-pink-100/80'
        )}
      >
        <div class="mb-3 text-3xl">{service.icon}</div>
        <h3 class="text-xl font-bold mb-2">{service.title}</h3>
        <p class="text-muted-foreground mb-4">{service.description}</p>

        <ul class="space-y-2 mb-6">
          {#each service.features as feature}
            <li class="flex items-center gap-2">
              <svg
                class="w-4 h-4 text-green-500"
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
          <span class="font-semibold">{service.price}</span>
          <Button variant="outline" href="/faq">Learn More</Button>
        </div>
      </div>
    {/each}
  </div>

  <div class="text-center p-8 rounded-lg border border-border/40 bg-neutral-100/50">
    <h2 class="text-2xl font-bold mb-3">Ready to Get Started?</h2>
    <p class="text-muted-foreground mb-6 max-w-2xl mx-auto">
      Join thousands of artists building their careers with our services.
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <Button size="lg" href="/sign-up">Get Started</Button>
      <Button size="lg" variant="outline" href="https://calendly.com/natehouk" target="_blank">
        Schedule a Call
      </Button>
    </div>
  </div>
</div>

<div
  class="absolute inset-0 -z-10 h-full w-full bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
/>
