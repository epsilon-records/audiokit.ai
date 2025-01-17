<script lang="ts">
  import { goto } from '$app/navigation';
  import { SignedIn, SignedOut } from 'svelte-clerk';
  import { toast } from 'svelte-sonner';
  import { page } from '$app/state';

  let { data } = $props();
  let email = $derived(data.email);
  let isAnnual = $state(true);
  let loadingTier = $state<string | null>(null);

  interface PricingTier {
    name: string;
    description: string;
    monthlyPrice: number;
    annualPrice: number;
    features: string[];
    highlighted?: boolean;
  }

  const pricingTiers: PricingTier[] = [
    {
      name: 'Basic Label',
      description: 'Perfect for individual artists and small labels getting started',
      monthlyPrice: 19,
      annualPrice: 99,
      features: [
        'Manage up to 5 artists',
        '5 team members per artist',
        '5GB media storage per artist',
        'Advanced analytics dashboard',
        'Release planning & scheduling',
        'Music distribution to major platforms',
        'Royalty tracking & reporting',
        'Contract templates & e-signing',
        'Email support within 24 hours',
        'Standard API access',
        'Basic integrations',
      ],
    },
    {
      name: 'Pro Label',
      description: 'Advanced features for growing professional labels',
      monthlyPrice: 79,
      annualPrice: 599,
      highlighted: true,
      features: [
        'Unlimited artists',
        'Unlimited team members',
        'Unlimited storage',
        'Advanced analytics dashboard',
        'Release planning & scheduling',
        'Music distribution to major platforms',
        'Royalty tracking & reporting',
        'Contract templates & e-signing',
        '24/7 Slack channel support',
        'Priority API access',
        'Advanced integrations',
        'Custom workflows',
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
        toast.error('Failed to start checkout process. Please try again.');
      } finally {
        loadingTier = null;
      }
    } else {
      await goto('/sign-up');
    }
  }
</script>

<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
  <div class="text-center">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl mb-8">
      Simple, transparent pricing
    </h1>
  </div>

  <div class="flex justify-center items-center gap-3 mb-8">
    <span class:text-gray-900={!isAnnual} class:text-gray-500={isAnnual}>Monthly</span>
    <button
      type="button"
      class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 bg-primary"
      role="switch"
      aria-checked={isAnnual}
      onclick={() => (isAnnual = !isAnnual)}
    >
      <span
        class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
        class:translate-x-5={isAnnual}
        class:translate-x-0={!isAnnual}
      />
    </button>
    <span class:text-gray-500={!isAnnual} class:text-gray-900={isAnnual}>
      Annual
      <span class="text-green-600 font-medium">
        (Save up to ${Math.max(savings.basic, savings.pro)}/mo)
      </span>
    </span>
  </div>

  <div class="grid md:grid-cols-2 gap-6">
    {#each pricingTiers as tier}
      <div
        class="relative flex flex-col rounded-xl border p-6 shadow-sm"
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
            <span class="text-4xl font-bold tracking-tight text-gray-900">
              ${isAnnual ? tier.annualPrice : tier.monthlyPrice}
            </span>
            <span class="ml-1 text-lg font-semibold text-gray-600">
              {isAnnual ? '/year' : '/month'}
            </span>
          </p>
          {#if isAnnual}
            <p class="mt-1 text-sm text-green-600">
              Save ${(tier.monthlyPrice * 12 - tier.annualPrice).toFixed(2)} with annual billing
            </p>
          {/if}
        </div>

        <ul role="list" class="mb-6 space-y-3 flex-1">
          {#each tier.features as feature}
            <li class="flex gap-2">
              <svg
                class="h-5 w-5 flex-none text-primary"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span class="text-sm text-gray-600">{feature}</span>
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
