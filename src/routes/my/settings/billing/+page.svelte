<script lang="ts">
  import SettingsContainer from '$lib/components/SettingsContainer.svelte';
  import { Button } from '$lib/components/ui/button';
  import { Card } from '$lib/components/ui/card';
  import { enhance } from '$app/forms';

  let { data } = $props();
  let loading = $state(false);

  const features = {
    basic: ['Basic Distribution', '2 Releases/Year', 'Standard Support'],
    pro: ['Unlimited Distribution', 'Priority Support', 'Marketing Tools', 'Analytics Dashboard'],
    enterprise: [
      'Custom Distribution',
      'Dedicated Account Manager',
      'Advanced Analytics',
      'Priority Release Schedule',
      'Custom Marketing Campaigns',
    ],
  };

  async function handleAction(action: 'subscribe' | 'manage', priceId?: string) {
    loading = true;
    try {
      const formData = new FormData();
      if (priceId) formData.append('priceId', priceId);

      const response = await fetch(`?/${action}`, {
        method: 'POST',
        body: formData,
      });

      const { url } = await response.json();
      if (url) window.location.href = url;
    } catch (error) {
      console.error(`${action} error:`, error);
    } finally {
      loading = false;
    }
  }
</script>

<SettingsContainer title="Billing & Subscription">
  <svelte:fragment slot="description">Manage your subscription and billing details.</svelte:fragment
  >

  {#if data.currentPlan}
    <div class="mb-8 p-6 bg-green-100 rounded-lg border-2 border-green-200">
      <h2 class="text-2xl font-bold mb-4">Current Subscription</h2>
      <div class="flex justify-between items-center">
        <div>
          <p class="text-lg font-semibold">{data.currentPlan.plan.product.name}</p>
          <p class="text-sm text-muted-foreground">
            Next billing date: {new Date(
              data.currentPlan.current_period_end * 1000,
            ).toLocaleDateString()}
          </p>
        </div>
        <Button variant="outline" on:click={() => handleAction('manage')} disabled={loading}>
          Manage Subscription
        </Button>
      </div>
    </div>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
    {#each data.plans as plan}
      <Card class="relative p-6 {plan.isPopular ? 'border-primary' : ''}">
        {#if plan.isPopular}
          <div
            class="absolute top-0 right-0 bg-primary text-primary-foreground px-3 py-1 text-sm rounded-bl-lg rounded-tr-lg"
          >
            Popular
          </div>
        {/if}

        <h3 class="text-2xl font-bold">{plan.name}</h3>
        <p class="text-3xl font-bold mt-4">
          ${plan.price}<span class="text-sm font-normal">/{plan.interval}</span>
        </p>
        <p class="mt-2 text-sm text-muted-foreground">{plan.description}</p>

        <ul class="mt-6 space-y-2">
          {#each plan.features as feature}
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

        <Button
          class="w-full mt-6"
          variant={plan.isPopular ? 'default' : 'outline'}
          disabled={loading || data.currentPlan?.plan.product.id === plan.productId}
          on:click={() => handleAction('subscribe', plan.id)}
        >
          {#if data.currentPlan?.plan.product.id === plan.productId}
            Current Plan
          {:else}
            {loading ? 'Processing...' : `Subscribe to ${plan.name}`}
          {/if}
        </Button>
      </Card>
    {/each}
  </div>
</SettingsContainer>
