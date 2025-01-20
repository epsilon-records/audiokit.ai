<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { cn } from '$lib/utils';
  import { fade, fly } from 'svelte/transition';

  let services = $state([
    {
      title: 'Digital Distribution',
      description: 'Distribute your music globally with AI-powered optimization',
      features: [
        'Unlimited releases on 200+ platforms',
        'AI-driven release timing',
        'Smart royalty splitting',
        'Automated metadata optimization',
      ],
      icon: '🎵',
      price: '$99/year',
      color: 'yellow',
      gradient: 'from-yellow-500/20 to-amber-500/20',
    },
    {
      title: 'Marketing & Promotion',
      description: 'AI-powered promotion strategies for maximum impact',
      features: [
        'AI playlist matching algorithm',
        'Social media content generation',
        'Targeted PR campaigns',
        'Fan engagement analytics',
      ],
      icon: '🚀',
      price: '$199/release',
      color: 'cyan',
      gradient: 'from-cyan-500/20 to-blue-500/20',
    },
    {
      title: 'Artist Development',
      description: 'Data-driven career growth strategies',
      features: [
        'AI market analysis',
        'Personalized growth roadmap',
        'Brand identity development',
        'Release strategy optimization',
      ],
      icon: '⭐',
      price: 'Custom',
      color: 'green',
      gradient: 'from-green-500/20 to-emerald-500/20',
    },
    {
      title: 'Analytics & Insights',
      description: 'AI-powered performance analytics',
      features: [
        'Real-time streaming analytics',
        'Audience behavior prediction',
        'Revenue forecasting',
        'Competitive analysis',
      ],
      icon: '📊',
      price: 'Free',
      color: 'pink',
      gradient: 'from-pink-500/20 to-rose-500/20',
    },
  ]);
</script>

<div class="relative">
  <div
    class="absolute inset-0 z-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>
  <div class="container max-w-6xl mx-auto px-4 py-16 relative z-10">
    <div class="text-center mb-12" in:fade={{ duration: 800 }}>
      <div class="bg-white inline-block">
        <h1
          class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-violet-500"
        >
          Services That Scale With You
        </h1>
      </div>
      <p class="bg-white text-muted-foreground max-w-2xl mx-auto text-lg">
        Leverage AI-powered tools and expert guidance to build a successful music career in the
        digital age.
      </p>
    </div>

    <div class="grid md:grid-cols-2 gap-8 mb-16">
      {#each services as service, i}
        <div
          in:fly={{ y: 20, duration: 600, delay: i * 100 }}
          class={cn(
            'group p-8 rounded-xl border border-border/40 transition-all hover:scale-[1.02] hover:shadow-lg relative z-20',
            'bg-gradient-to-br bg-background/80 backdrop-blur-sm',
            service.gradient
          )}
        >
          <div class="mb-4 text-4xl">{service.icon}</div>
          <h3 class="text-2xl font-bold mb-3">{service.title}</h3>
          <p class="text-muted-foreground mb-6 text-lg">{service.description}</p>

          <ul class="space-y-3 mb-8">
            {#each service.features as feature}
              <li class="flex items-center gap-3">
                <svg
                  class="w-5 h-5 text-primary"
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
                <span class="text-base">{feature}</span>
              </li>
            {/each}
          </ul>

          <div class="flex items-center justify-between mt-auto">
            <span class="text-xl font-semibold">{service.price}</span>
            <Button variant="outline" href="/faq" class="hover:bg-background/80">Learn More</Button>
          </div>
        </div>
      {/each}
    </div>

    <div
      in:fade={{ duration: 800, delay: 400 }}
      class="text-center p-12 rounded-xl border border-border/40 bg-gradient-to-br from-primary/5 to-blue-500/5 backdrop-blur-sm"
    >
      <h2 class="text-3xl font-bold mb-4">Ready to Transform Your Music Career?</h2>
      <p class="text-muted-foreground mb-8 max-w-2xl mx-auto text-lg">
        Join thousands of artists using our AI-powered platform to reach new heights in their music
        careers.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <Button size="lg" class="text-lg px-8">Get Started</Button>
        <Button
          size="lg"
          variant="outline"
          href="https://cal.com/audiokit"
          target="_blank"
          class="text-lg px-8"
        >
          Book a Consultation
        </Button>
      </div>
    </div>
  </div>
</div>
