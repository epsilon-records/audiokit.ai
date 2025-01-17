<script lang="ts">
  let isAnnual = $state(false);

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
      name: 'Basic',
      description: 'Perfect for individuals and small teams getting started',
      monthlyPrice: 29,
      annualPrice: 290, // 2 months free
      features: [
        'Up to 5 team members',
        '10GB storage',
        'Basic analytics',
        'API access',
        'Email support',
        'Basic integrations',
      ],
    },
    {
      name: 'Pro',
      description: 'Advanced features for growing businesses',
      monthlyPrice: 79,
      annualPrice: 790, // 2 months free
      highlighted: true,
      features: [
        'Unlimited team members',
        'Unlimited storage',
        'Advanced analytics',
        'Priority API access',
        '24/7 phone & email support',
        'Advanced integrations',
        'Custom workflows',
      ],
    },
  ];

  const savings = $derived({
    basic: Math.round((pricingTiers[0].monthlyPrice * 12 - pricingTiers[0].annualPrice) / 12),
    pro: Math.round((pricingTiers[1].monthlyPrice * 12 - pricingTiers[1].annualPrice) / 12),
  });
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
  <div class="text-center">
    <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
      Simple, transparent pricing
    </h1>
    <p class="mt-4 text-xl text-gray-600">Start free for 14 days. No credit card required.</p>
  </div>

  <div class="mt-12 flex justify-center items-center gap-3">
    <span class:text-gray-900={!isAnnual} class:text-gray-500={isAnnual}>Monthly</span>
    <button
      type="button"
      class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 bg-primary"
      role="switch"
      aria-checked={isAnnual}
      on:click={() => (isAnnual = !isAnnual)}
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

  <div class="mt-12 grid md:grid-cols-2 gap-8 lg:gap-12">
    {#each pricingTiers as tier}
      <div
        class="relative flex flex-col rounded-2xl border p-8 shadow-sm"
        class:ring-2={tier.highlighted}
        class:ring-primary={tier.highlighted}
      >
        {#if tier.highlighted}
          <div class="absolute -top-4 right-8">
            <span
              class="inline-flex items-center rounded-full bg-primary px-3 py-0.5 text-sm font-medium text-white"
            >
              Popular
            </span>
          </div>
        {/if}

        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900">{tier.name}</h3>
          <p class="mt-2 text-gray-600">{tier.description}</p>
        </div>

        <div class="mb-6">
          <p class="flex items-baseline">
            <span class="text-5xl font-bold tracking-tight text-gray-900">
              ${isAnnual ? Math.round(tier.annualPrice / 12) : tier.monthlyPrice}
            </span>
            <span class="ml-1 text-xl font-semibold text-gray-600">/month</span>
          </p>
          {#if isAnnual}
            <p class="mt-1 text-sm text-green-600">
              Save ${isAnnual ? (tier.monthlyPrice * 12 - tier.annualPrice) / 12 : 0}/mo with annual
              billing
            </p>
          {/if}
        </div>

        <ul role="list" class="mb-8 space-y-4 flex-1">
          {#each tier.features as feature}
            <li class="flex gap-3">
              <svg
                class="h-6 w-6 flex-none text-primary"
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
              <span class="text-gray-600">{feature}</span>
            </li>
          {/each}
        </ul>

        <a
          href="/signup"
          class="block w-full rounded-lg px-4 py-2.5 text-center text-sm font-semibold transition-colors {tier.highlighted
            ? 'bg-primary text-white hover:bg-primary/90'
            : 'bg-gray-50 text-gray-900 hover:bg-gray-100'}"
        >
          Start {tier.name} trial
        </a>
      </div>
    {/each}
  </div>

  <p class="mt-12 text-center text-sm text-gray-600">
    All plans include a 14-day free trial. No credit card required.
    <a href="/terms" class="font-medium text-primary hover:underline">Terms apply</a>
  </p>
</div>
