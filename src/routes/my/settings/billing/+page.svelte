<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Card } from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Check, Sparkles, Star } from 'lucide-svelte';

  interface PricingPlan {
    id: string;
    name: string;
    price: number;
    interval: 'month' | 'year';
    features: string[];
    ctaText: string;
    emoji: string;
    popular?: boolean;
  }

  const plans: PricingPlan[] = [
    {
      id: 'monthly',
      name: 'Monthly Plan',
      price: 19,
      interval: 'month',
      emoji: '🚀',
      features: [
        'Full access to Epsilon Distribution',
        'Priority support',
        'Advanced analytics',
        'Custom integrations',
        'Team collaboration tools',
        '30-day free trial',
      ],
      ctaText: 'Start Monthly Plan',
    },
    {
      id: 'yearly',
      name: 'Annual Plan',
      price: 99,
      interval: 'year',
      emoji: '⭐',
      popular: true,
      features: [
        'Everything in Monthly Plan',
        '~$8.25/month (Save 57%)',
        'Extended API limits',
        'Premium support',
        'Advanced reporting',
        '30-day free trial',
      ],
      ctaText: 'Start Annual Plan',
    },
  ];
</script>

<SettingsContainer title="Billing & Subscription">
  <svelte:fragment slot="description">
    Choose the plan that best fits your needs. All plans include a 30-day free trial.
  </svelte:fragment>

  <div class="space-y-6">
    <div class="grid md:grid-cols-2 gap-6">
      {#each plans as plan}
        <Card
          class="relative p-6 flex flex-col border-2 {plan.popular
            ? 'border-primary'
            : 'border-border'} shadow-lg hover:shadow-xl transition-all duration-300"
        >
          {#if plan.popular}
            <div class="absolute -top-3 left-1/2 -translate-x-1/2">
              <Badge
                variant="default"
                class="bg-primary text-primary-foreground flex items-center gap-1"
              >
                <Sparkles class="h-3 w-3" />
                <span>Most Popular</span>
              </Badge>
            </div>
          {/if}

          <div class="mb-4">
            <div class="flex items-center gap-2">
              <span class="text-2xl">{plan.emoji}</span>
              <h3 class="text-lg font-semibold">{plan.name}</h3>
            </div>
            <div class="mt-4">
              <span class="text-4xl font-bold text-primary">${plan.price}</span>
              <span class="text-muted-foreground">/{plan.interval}</span>
            </div>
          </div>

          <ul class="space-y-3 my-6 flex-grow">
            {#each plan.features as feature}
              <li class="flex items-center gap-2">
                <div class="rounded-full bg-primary/10 p-1">
                  <Check class="h-4 w-4 text-primary" />
                </div>
                <span class="text-sm">{feature}</span>
              </li>
            {/each}
          </ul>

          <Button
            class="w-full {plan.popular ? 'bg-primary hover:bg-primary/90' : ''}"
            variant={plan.popular ? 'default' : 'outline'}
            size="lg"
            href={plan.id === 'monthly'
              ? 'https://buy.stripe.com/14k9CLflu2k3eVGcMO'
              : 'https://buy.stripe.com/aEU9CLa1abUDcNy145'}
          >
            {plan.ctaText}
          </Button>
        </Card>
      {/each}
    </div>

    <div class="mt-12 text-center space-y-4">
      <div class="flex items-center justify-center gap-2 text-primary">
        <Star class="h-5 w-5" />
        <p class="font-medium">30-Day Free Trial</p>
      </div>
      <p class="text-sm text-muted-foreground">Try any plan risk-free. Cancel anytime.</p>
    </div>
  </div>
</SettingsContainer>
