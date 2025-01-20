<script lang="ts">
  import { goto } from '$app/navigation';
  import { SignedIn, SignedOut } from 'svelte-clerk';
  import { toast } from 'svelte-sonner';
  import { siDiscord } from 'simple-icons';
  import { Button } from './ui/button';

  let { email, title, description } = $props();

  let isAnnual = $state(true);
  let loadingTier = $state<string | null>(null);

  interface PricingTier {
    name: string;
    description: string;
    monthlyPrice: number;
    annualPrice: number;
    features: { text: string; icon: string }[];
    highlighted?: boolean;
  }

  const pricingTiers: PricingTier[] = [
    {
      name: '🎵 Individual Artist',
      description:
        'Perfect for solo artists and creators ready to share their music with the world',
      monthlyPrice: 19,
      annualPrice: 99,
      features: [
        { text: 'Manage one individual artist', icon: '👤' },
        { text: 'Music distribution to all major platforms', icon: '🎧' },
        { text: 'Keep 100% of your music royalties', icon: '💰' },
        { text: 'Up to 5 team members', icon: '🤝' },
        { text: '5GB media storage', icon: '💾' },
        { text: 'Basic analytics dashboard', icon: '📊' },
        { text: 'Release planning & scheduling', icon: '📅' },
        { text: 'Royalty tracking & reporting', icon: '💰' },
        { text: 'Contract templates & e-signing', icon: '📝' },
        { text: '24/7 Discord channel support', icon: 'discord' },
        { text: 'Limited API access', icon: '🔑' },
      ],
    },
    {
      name: '⭐ Record Label',
      description:
        'Powerful tools for professional labels managing multiple artists and releases at scale',
      monthlyPrice: 79,
      annualPrice: 599,
      highlighted: true,
      features: [
        { text: 'Manage unlimited artists', icon: '👥' },
        { text: 'Music distribution to all major platforms', icon: '🎧' },
        { text: 'Keep 100% of your music royalties', icon: '💰' },
        { text: 'Unlimited team members', icon: '🤝' },
        { text: 'Unlimited storage', icon: '💾' },
        { text: 'Advanced analytics dashboard', icon: '📊' },
        { text: 'Release planning & scheduling', icon: '📅' },
        { text: 'Royalty tracking & reporting', icon: '💰' },
        { text: 'Contract templates & e-signing', icon: '📝' },
        { text: '24/7 Discord channel support', icon: 'discord' },
        { text: 'Priority API access', icon: '🔑' },
        { text: 'Advanced integrations', icon: '🔌' },
        { text: 'Custom workflows', icon: '⚡' },
      ],
    },
  ];

  const savings = $derived({
    basic: Math.round((pricingTiers[0].monthlyPrice * 12 - pricingTiers[0].annualPrice) / 12),
    pro: Math.round((pricingTiers[1].monthlyPrice * 12 - pricingTiers[1].annualPrice) / 12),
  });

  async function handleCheckout(tier: PricingTier) {
    loadingTier = tier.name;
    if (email) {
      try {
        const payload = {
          tier: tier.name,
          isAnnual,
          email: email,
        };
        console.log(payload);

        const response = await fetch('/api/create-checkout-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error('Failed to create checkout session');
        }

        const { url } = await response.json();
        window.location.href = url;
      } catch (err) {
        console.error(err);
        toast.error('Failed to start checkout process. Please try again.');
      } finally {
        loadingTier = null;
      }
    } else {
      await goto('/sign-up');
    }
  }
</script>

<div class="relative">
  <div
    class="absolute inset-0 bg-[radial-gradient(#0f131750_1px,transparent_1px)] [background-size:16px_16px]"
  ></div>
  <div class="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-12">
    <div class="text-center mb-8 rounded-xl shadow-sm" in:fade={{ duration: 800 }}>
      <div class="bg-white inline-block">
        <h1
          class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-violet-500"
        >
          {title}
        </h1>
      </div>
      <p class="bg-white text-muted-foreground max-w-2xl mx-auto text-lg">
        {description}
      </p>
    </div>

    <div class="flex flex-col items-center gap-2 mb-6">
      <div class="bg-white px-4 py-2 rounded-lg">
        <div class="flex items-center gap-3">
          <span class:text-gray-900={!isAnnual} class:text-gray-500={isAnnual}>Monthly</span>
          <input
            type="checkbox"
            class="toggle toggle-primary"
            checked={isAnnual}
            onchange={() => (isAnnual = !isAnnual)}
            aria-label="Toggle billing period"
          />
          <span class:text-gray-500={!isAnnual} class:text-gray-900={isAnnual}>Annual</span>
        </div>
        {#if isAnnual}
          <span class="text-green-600 font-medium text-center mt-1">
            Save up to ${Math.max(savings.basic, savings.pro)}/month
          </span>
        {/if}
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
      {#each pricingTiers as tier, i}
        <div
          in:fly={{ y: 20, duration: 600, delay: i * 200 }}
          class="relative flex flex-col rounded-xl border p-6 shadow-sm bg-white"
          class:ring-2={tier.highlighted}
          class:ring-primary={tier.highlighted}
        >
          {#if tier.highlighted}
            <div class="absolute -top-3 right-6">
              <span
                class="inline-flex items-center rounded-full bg-primary px-3 py-0.5 text-sm font-medium text-white"
              >
                Popular
              </span>
            </div>
          {/if}

          <div class="mb-4">
            <h3 class="text-xl font-bold text-gray-900">{tier.name}</h3>
            <p class="mt-2 text-sm text-gray-600">{tier.description}</p>
          </div>

          <div class="mb-4">
            <p class="flex items-baseline">
              <span
                class="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-emerald-400"
              >
                ${isAnnual ? tier.annualPrice : tier.monthlyPrice}
              </span>
              <span class="ml-1 text-lg font-semibold text-gray-600">
                {isAnnual ? '/year' : '/month'}
              </span>
            </p>
            {#if isAnnual}
              <p class="mt-1 text-sm text-emerald-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Save ${(tier.monthlyPrice * 12 - tier.annualPrice).toFixed(2)} with annual billing
              </p>
            {/if}
          </div>

          <ul role="list" class="mb-6 space-y-3 flex-1">
            {#each tier.features as feature}
              <li class="flex gap-3 items-center">
                <svg
                  class="h-5 w-5 flex-none text-emerald-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="2"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span class="text-sm text-gray-600">
                  <span class="mr-2">
                    {#if feature.icon === 'discord'}
                      <svg
                        role="img"
                        viewBox="0 0 24 24"
                        class="inline-block w-4 h-4 text-[#5865F2]"
                      >
                        <path fill="currentColor" d={siDiscord.path} />
                      </svg>
                    {:else}
                      {feature.icon}
                    {/if}
                  </span>
                  {feature.text}
                </span>
              </li>
            {/each}
          </ul>

          <SignedIn>
            <button
              type="button"
              onclick={() => handleCheckout(tier)}
              disabled={loadingTier === tier.name}
              class="block w-full rounded-lg px-4 py-2 text-center text-sm font-semibold transition-colors {tier.highlighted
                ? 'bg-primary text-white hover:bg-primary/90'
                : 'bg-gray-50 text-gray-900 hover:bg-gray-100'}"
            >
              {#if loadingTier === tier.name}
                <span class="inline-flex items-center">
                  <svg
                    class="animate-spin -ml-1 mr-3 h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    />
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Processing...
                </span>
              {:else}
                Subscribe to {tier.name}
              {/if}
            </button>
          </SignedIn>

          <SignedOut>
            <a
              href="/sign-up"
              class="block w-full rounded-lg px-4 py-2 text-center text-sm font-semibold transition-colors {tier.highlighted
                ? 'bg-primary text-white hover:bg-primary/90'
                : 'bg-gray-50 text-gray-900 hover:bg-gray-100'}"
            >
              Subscribe to {tier.name}
            </a>
          </SignedOut>
        </div>
      {/each}
    </div>
  </div>
  <div class="text-center py-12 rounded-lg" in:fade={{ duration: 800, delay: 200 }}>
    <div class="flex flex-col items-center gap-4 relative z-20">
      <h2 class="bg-white px-6 py-2 rounded-lg text-4xl font-semibold text-primary">
        Need help choosing a plan?
      </h2>
      <div class="bg-white px-6 py-2 rounded-lg">
        <p class="text-muted-foreground">
          Talk to our music industry experts about finding the right fit for your goals.
        </p>
      </div>
      <div class="flex items-center justify-center gap-4">
        <Button href="/faq" variant="default" class="text-lg secondary hover:opacity-90">
          Read the FAQ
        </Button>
        <Button href="mailto:support@audiokit.ai" variant="outline" class="text-lg gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
          Contact Support
        </Button>
      </div>
    </div>
  </div>
</div>
